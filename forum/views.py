# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse

# Create your views here.
from forum.models import Thread, Message

from promotions.models import Lesson
from skills.models import Skill
from users.models import Professor, Student

from dashboard import get_thread_set


class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)


def require_login(function):
    return login_required(function, login_url="/accounts/usernamelogin")


@require_GET
@require_login
def forum_dashboard(request):
    threads = get_thread_set(request.user)
    return render(request, "forum/dashboard.haml", {
        "user": request.user,
        "threads": threads
    })


@require_login
def create_thread(request):
    """
    GET: return the page to create a thread
    POST: create a thread
    """
    if request.method == 'GET':
        return get_create_thread_page(request)

    if request.method == 'POST':
        return post_create_thread(request)


@require_GET
@require_login
def get_users(request):
    users = [
        {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        } for user in User.objects.all()
    ]

    return JsonResponse({"data": users})


@require_GET
@require_login
def get_professors(request):
    lessons = None
    user = request.user
    professor = None
    student = None
    professors = []
    if Student.objects.filter(user=user).exists():
        student = Student.objects.get(user=user)
        lessons = student.lesson_set.all()
    elif Professor.objects.filter(user=user).exists():
        professor = Professor.objects.get(user=user)
        lessons = professor.lesson_set.all()

    for lesson in lessons:
        for prof in lesson.professors.all():
            if (professor is not None and professor.id != prof.id) or professor is None:
                professors.append({
                    "id": prof.id,
                    "username": prof.user.username,
                    "first_name": prof.user.first_name,
                    "last_name": prof.user.last_name
                })

    return JsonResponse({"data": professors})


@require_login
@require_GET
def get_lessons(request):
    user = request.user
    if Student.objects.filter(user=user).exists():
        student = Student.objects.get(user=user)
        lessons = student.lesson_set.all()
    elif Professor.objects.filter(user=user).exists():
        professor = Professor.objects.get(user=user)
        lessons = professor.lesson_set.all()

    lesson_list = [
        {
            "id": lesson.id,
            "name": lesson.name
        }
        for lesson in lessons
    ]

    return JsonResponse({"data": lesson_list})


def get_skills(request):
    user = request.user
    if Student.objects.filter(user=user).exists():
        student = Student.objects.get(user=user)
        lessons = student.lesson_set.all()
    elif Professor.objects.filter(user=user).exists():
        professor = Professor.objects.get(user=user)
        lessons = professor.lesson_set.all()
    else:
        lessons = []

    skills = set()
    sections = set()
    stages = [lesson.stage for lesson in lessons]
    for stage in stages:
        for skill in stage.skills.all():
            skills.add(skill)
            sections.add(skill.section)

    skills = list(skills)
    skills.sort(key=lambda x: x.name)

    sections = list(sections)
    sections.sort(key=lambda x: x.name)

    return skills, sections


def get_create_thread_page(request):

    skills, sections = get_skills(request)

    return render(request, "forum/new_thread.haml", {'errors': [], "data": {
        'title': "",
        'visibility': "private",
        'visibdata': "",
        'skills': skills,
        'sections': sections,
        'content': ""
    }})


def post_create_thread(request):
    errors = []
    params = deepValidateAndFetch(request, errors)

    if len(errors) == 0:

        with transaction.atomic():
            thread = Thread(title=params['title'], author=params['author'], section_id=params['section'])

            if params['visibility'] == 'private':
                thread.recipient = params['recipient']

            if params['visibility'] == 'class':
                thread.lesson = params['lesson']

            if params['visibility'] == 'public':
                thread.professor = params['professor']

            thread.save()

            if params['skills_fetched']:
                thread.skills = params['fetched_skills']
                thread.save()

            original_message = Message(content=params['content'], thread=thread, author=params['author'])
            original_message.save()

        return redirect('/forum/thread/' + str(thread.id))

    else:
        return render(request, "forum/new_thread.haml", {"errors": errors, "data": params})




class ThreadForm(forms.Form):
    section = forms.CharField()
    title = forms.CharField()
    visibdata = forms.CharField()
    content = forms.CharField()


def deepValidateAndFetch(request, errors):
    params = {}
    form = ThreadForm(request.POST)


    form.is_valid()

    params['visibility'] = request.POST.get('visibility')
    params['skills_fetched'] = False

    try:
        params['section'] = form.cleaned_data['section']
    except:
        params['section'] = None


    try:
        params['skills'] = request.POST.getlist('skills')
    except:
        params['skills'] = []

    try:
        params['title'] = form.cleaned_data['title']
    except:
        params['title'] = ""
        errors.append({"field": "title", "msg": "Le titre du sujet ne peut pas être vide"})

    try:
        params['visibdata'] = form.cleaned_data['visibdata']
    except:
        params['visibdata'] = ""
        errors.append({"field": "visibdata", "msg": "Ce champs ne peut pas être vide"})

    try:
        params['content'] = form.cleaned_data['content']
    except:
        params['content'] = ""
        errors.append({"field": "content", "msg": "Le premier message du sujet ne peut pas être vide"})

    # Shouldn't fail with require_login
    params['author'] = User.objects.get(pk=request.user.id)

    if params['visibility'] not in ["private", "class", "public"]:
        errors.append({"field": "visibility", "msg": "Type de visibilité invalide"})

    if params['visibdata'] != "":
        if params['visibility'] == "private":
            try:
                params['recipient'] = User.objects.get(pk=params['visibdata'])
            except:
                errors.append({"field": "visibdata", "msg": "Destinataire inconnu"})

        if params['visibility'] == "class":
            try:
                params['lesson'] = Lesson.objects.get(pk=params['visibdata'])
            except:
                errors.append({"field": "visibdata", "msg": "Classe inconnue"})

        if params['visibility'] == "public":
            try:
                params['professor'] = Professor.objects.get(pk=params['visibdata'])
            except:
                errors.append({"field": "visibdata", "msg": "Professeur inconnu"})

    if len(params['skills']) > 0:
        try:
            params['fetched_skills'] = Skill.objects.filter(pk__in=params['skills'])
            params['skills_fetched'] = True
        except:
            errors.append(
                {"field": "skills", "msg": "Compétence(s) inconnue(s) ou mal formée(s) (format: id1 id2 ...)"})

    return params


@require_login
def thread(request, id):
    """
    GET method: return the page of a thread
    POST method: reply to a thread
    """
    if request.method == 'GET':
        return get_thread(request, id)

    if request.method == 'POST':
        return reply_thread(request, id)


def get_thread(request, id):
    thread = get_object_or_404(Thread, pk=id)
    messages = thread.messages()

    reply_to = request.GET.get('reply_to')

    return render(request, "forum/thread.haml", {
        "user": request.user,
        "thread": thread,
        "messages": messages,
        "reply_to": reply_to
    })


def reply_thread(request, id):
    thread = get_object_or_404(Thread, pk=id)
    message_id = request.GET.get('reply_to')

    form = MessageReplyForm(request.POST)  # request.Post contains the data we want
    author = User.objects.get(pk=request.user.id)
    if form.is_valid():
        content = form.cleaned_data['content']
        message = Message.objects.create(content=content, thread=thread, author=author)

        if message_id is not None:
            parent_message = get_object_or_404(Message, pk=message_id)
            message.parent_message = parent_message

        message.save()
        return redirect(message)
    else:
        return redirect(thread)  # TODO: error message
