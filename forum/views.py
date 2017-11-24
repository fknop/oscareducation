# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.timezone import utc
from django.views.decorators.http import require_POST, require_GET

from notification.notif_types import NOTIF_TYPES
from notification.notification_manager import NOTIF_MEDIUM, sendNotification

from django.http import JsonResponse


# Create your views here.
from numpy.ma import copy

from forum.models import Thread, Message, LastThreadVisit, MessageAttachment

from promotions.models import Lesson
from skills.models import Skill, Section
from resources.models import Resource, KhanAcademy, Sesamath
from users.models import Professor, Student

from dashboard import get_thread_set


class MessageReplyForm(forms.ModelForm):
    file = forms.FileField(required=False, label='file')

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
                p = {
                    "id": prof.id,
                    "username": prof.user.username,
                    "first_name": prof.user.first_name,
                    "last_name": prof.user.last_name
                }
                professors.append(frozenset(p.items()))

    professors = list([dict(prof) for prof in set(professors)])
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


@require_login
@require_GET
def get_resources(request):
    return JsonResponse({"data": get_resources_list(request)})


def get_resources_list(request):
    skills, sections = get_skills(request)
    selected_skills, selected_section = get_selected_skills_section(request)
    filtered_skills = [skill for skill in skills if skill.id in selected_skills] \
        if selected_skills \
        else skills
    filtered_sections = [section for section in sections if section.id in selected_section] \
        if selected_section \
        else sections

    resources = set()
    for skill_section in filtered_skills+filtered_sections:
        for resource in skill_section.resource.all():
            if "from" in resource.content:
                if resource.content["from"] == "skills_sesamathskill":
                    special_resource = Sesamath.objects.get(pk=resource.content["referenced"])
                elif resource.content["from"] == "skills_khanacademyvideoskill":
                    special_resource = KhanAcademy.objects.get(pk=resource.content["referenced"])
                resources.add(
                    frozenset({
                        "id": resource.id,
                        "title": special_resource.title
                    }.items())
                )
            else:
                resources.add(
                    frozenset({
                        "id": resource.id,
                        "title": resource.content["title"]
                    }.items())
                )

    return [dict(res) for res in set(resources)]


def get_selected_resource(request):
    selected_skills, selected_sections = get_selected_skills_section(request)
    selected_visibdata = get_selected_visibdata(request)

    requested_resource = request.GET.get('resource', '')
    if requested_resource:
        resource = Resource.objects.get(pk=requested_resource)
        linked_skills = resource.skill_resource.all()
        linked_sections = resource.section_resource.all()
        return resource.id, [skill.id for skill in linked_skills], [section.id for section in linked_sections], \
               resource.added_by_id
    return '', selected_skills, selected_sections, selected_visibdata


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

            if skill.section is not None:
                sections.add(skill.section)

    skills = list(skills)
    skills.sort(key=lambda x: x.name)

    sections = list(sections)
    sections.sort(key=lambda x: x.name)

    return skills, sections


def get_selected_skills_section(request):
    skills = request.GET.getlist('skills[]', [])
    section = request.GET.get('section', [])
    return [int(skill) for skill in skills if skill and skill.isdigit()], [int(section)] \
        if section and section.isdigit() else []


def get_selected_visibdata(request):
    res = request.GET.get('visibdata', None)
    if res:
        res = int(res) if res.isdigit() else None
    return res


def get_selected_visibility(request):
    visibility = request.GET.get('visibility', 'private')
    if visibility not in ['private', 'class', 'public']:
        visibility = 'private'
    return visibility


def get_create_thread_page(request):
    skills, sections = get_skills(request)
    resources = get_resources_list(request)
    selected_resource, selected_skills, selected_sections, selected_visibdata = get_selected_resource(request)
    visibility = get_selected_visibility(request)

    return render(request, "forum/new_thread.haml", {'errors': [], "data": {
        'title': request.GET.get('title', ''),
        'visibility': visibility,
        'visibdata': selected_visibdata,
        'skills': skills,
        'selected_skills': selected_skills,
        'sections': sections,
        'selected_sections': selected_sections,
        'content': "",
        'resources': resources,
        'selected_resource': selected_resource
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

            sendNotification(getWSNotificationForNewThread(thread))


            original_message = Message(content=params['content'], thread=thread, author=params['author'], created_date=utc.localize(datetime.now()), modified_date=utc.localize(datetime.now()))
            original_message.save()


            sendNotification(getNotificationForNewMessage(original_message))

        return redirect(thread)


    else:
        skills, sections = get_skills(request)
        params['skills'] = skills
        params['sections'] = sections

        if params['skills_fetched']:
            params['selected_skills'] = map(lambda x: x.id, params['fetched_skills'])
        else:
            params['selected_skills'] = []

        if params['section'] is not None:
            params['selected_section'] = int(params['section'])

        return render(request, "forum/new_thread.haml", {"errors": errors, "data": params})


def getWSNotificationForNewThread(thread):

    notif = {
        "medium": NOTIF_MEDIUM["WS"],
        "audience": [],
        "params": {
            "thread_id": str(thread.id),
            "thread_title": thread.title,
            "author": {
                "id": thread.author.id,
                "first_name": thread.author.first_name,
                "last_name": thread.author.last_name
            }
        }
    }

    if thread.professor != None:

        notif["type"] = NOTIF_TYPES["NEW_PUBLIC_FORUM_THREAD"]
        notif["params"]["classes"] = []

        try:
            for l in thread.professor.lesson_set.all():
                notif["audience"].append('notification-class-' + str(l.id))
                notif["params"]["classes"].append({
                    "id": l.id,
                    "name": l.name
                })
        except:
            pass

    elif thread.lesson != None:
        notif["type"] = NOTIF_TYPES["NEW_CLASS_FORUM_THREAD"]
        notif["audience"] = [ 'notification-class-' + str(thread.lesson.id) ]
        notif["params"]["class"] = {
            "id": thread.lesson.id,
            "name": thread.lesson.name
        }
    elif thread.recipient != None:
        notif["type"] = NOTIF_TYPES["NEW_PRIVATE_FORUM_THREAD"]
        notif["audience"] = [ 'notification-user-' + str(thread.recipient.id) ]

    return notif

def getNotificationForNewMessage(message):

    notif = getWSNotificationForNewThread(message.thread)

    notif["type"] = notif["type"].replace("thread", "message")
    notif["params"]["author"] = {
        "id": message.author.id,
        "first_name": message.author.first_name,
        "last_name": message.author.last_name
    }
    notif["params"]["msg_id"] = message.id

    if (message.thread.recipient != None) and (message.author != message.thread.author):
        notif["audience"] = ['notification-user-' + str(message.thread.author.id)]

    return notif

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
                {"field": "skills", "msg": "Compétence(s) inconnue(s) ou mal formée(s) (format: [id1, id2, ...])"})

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


def get_last_visit(user, thread):
    if LastThreadVisit.objects.filter(user=user, thread=thread).exists():
        last_visit = LastThreadVisit.objects.get(user=user, thread=thread)
        date = last_visit.last_visit
        last_visit.last_visit = utc.localize(datetime.now())
    else:
        last_visit = LastThreadVisit(user=user, thread=thread, last_visit=utc.localize(datetime.now()))
        date = utc.localize(datetime.min)
    last_visit.save()
    return date


def get_file(request):
    # Check if user as access to this file

    threads = get_thread_set(request.user)
    message = get_object_or_404(Message, pk=request.message.id)
    if message.thread not in threads:
        return HttpResponse(status=403)

    attachment = get_object_or_404(MessageAttachment, pk=request.message)

    filename = attachment.file.name.split('/')[-1]
    response = HttpResponse(attachment.file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return render();


def get_thread(request, id):
    thread = get_object_or_404(Thread, pk=id)
    messages = thread.messages()

    attachments = ()
    # for m in messages:
        # attachments += m.attachments()

    last_visit = get_last_visit(request.user, thread)
    reply_to = request.GET.get('reply_to')
    edit = request.GET.get('edit')

    if edit is not None:
        to_edit = get_object_or_404(Message, pk=edit)
        if not can_update(thread, to_edit, request.user):
            edit = None
        else:
            edit = to_edit.id

    return render(request, "forum/thread.haml", {
        "user": request.user,
        "thread": thread,
        "messages": messages,
        "reply_to": reply_to,
        "last_visit": last_visit,
        "attachments": attachments,
        "edit": edit
    })


def reply_thread(request, id):
    thread = get_object_or_404(Thread, pk=id)
    message_id = request.GET.get('reply_to')

    form = MessageReplyForm(request.POST)  # request.Post contains the data we want
    author = User.objects.get(pk=request.user.id)

    if form.is_valid():
        content = form.cleaned_data['content']

        message = Message.objects.create(content=content, thread=thread, author=author,
                                         created_date=utc.localize(datetime.now()), modified_date=utc.localize(datetime.now()))


        with transaction.atomic():
            message = Message.objects.create(content=content, thread=thread, author=author, created_date=utc.localize(datetime.now()), modified_date=utc.localize(datetime.now()))

            if message_id is not None:
                parent_message = get_object_or_404(Message, pk=message_id)
                message.parent_message = parent_message

            message.save()
            thread.modified_date = message.created_date
            thread.save()

        sendNotification(getNotificationForNewMessage(message))

        return redirect(message)
    else:
        return HttpResponse(status=400, content="Malformed request")


def can_update(thread, message, user):
    if message.thread_id != thread.id:
        return False

    if len(message.replies()) > 0:
        return False

    if thread.is_private():
        return message.author.id == user.id
    elif thread.is_public_professor():
        professor = Professor.objects.filter(user=user)
        return message.author.id == user.id or (professor is not None and thread.professor.id == professor.id)
    elif thread.is_public_lesson():
        professors = thread.lesson.professors.all()
        professor = Professor.objects.filter(user=user)
        condition = message.author.id == user.id
        if professor is not None:
            return condition or professor in professors
        else:
            return condition


@require_POST
@require_login
def edit_message(request, id, message_id):
    thread = get_object_or_404(Thread, pk=id)

    message = get_object_or_404(Message, pk=message_id)

    if not can_update(thread, message, request.user):
        return HttpResponse(status=403, content="Permissions missing to edit this message")

    content = request.POST.get("content")
    if content is None or len(content) == 0:
        return HttpResponse(status=400, content="Missing content")

    message.content = content
    message.save()

    return redirect(message)


@require_POST
@require_login
def delete_message(request, id, message_id):
    thread = get_object_or_404(Thread, pk=id)
    message = get_object_or_404(Message, pk=message_id)

    if not can_update(thread, message, request.user):
        return HttpResponse(status=403, content="Permissions missing to delete this message")

    message.delete()

    return redirect(thread)
