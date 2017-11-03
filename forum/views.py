# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST, require_GET

# Create your views here.
from forum.models import Thread, Message
from promotions.models import Lesson
from skills.models import Skill
from users.models import Professor
from dashboard import get_thread_set


@require_GET
def forum_dashboard(request):
    threads = get_thread_set(request.user)
    return render(request, "forum/dashboard.haml", {
        "user": request.user,
        "threads": threads
    })


def create_thread(request):
    """
    GET: return the page to create a thread
    POST: create a thread
    """
    if request.method == 'GET':
        return get_create_thread_page(request)

    if request.method == 'POST':
        return post_create_thread(request)


def get_create_thread_page(request):
    return render(request, "forum/new_thread.haml", { 'errors' : [], "data": {
            'title' : "",
            'visibility': "private",
            'visibdata' : "",
            'skills' : "",
            'content' : ""
        } })

def post_create_thread(request):

    errors = []
    params = deepValidateAndFetch(request, errors)

    if len(errors) == 0:

        with transaction.atomic():

            thread = Thread(title=params['title'], author=params['author'])

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
        return render(request, "forum/new_thread.haml", { "errors" : errors, "data": params })

class ThreadForm(forms.Form):
    title = forms.CharField()
    visibdata = forms.CharField()
    skills = forms.CharField()
    content = forms.CharField()

def deepValidateAndFetch(request, errors):

    params = {}
    form = ThreadForm(request.POST)

    form.is_valid()

    params['visibility'] = request.POST.get('visibility')
    params['skills_fetched'] = False

    try:
        params['skills'] = form.cleaned_data['skills']
    except:
        params['skills'] = ""

    try:
        params['title'] = form.cleaned_data['title']
    except:
        params['title'] = ""
        errors.append({ "field": "title", "msg" :"Le titre du sujet ne peut pas être vide"})

    try:
        params['visibdata'] = form.cleaned_data['visibdata']
    except:
        params['visibdata'] = ""
        errors.append({ "field": "visibdata", "msg" :"Le paramètre de visibilité ne peut pas être vide"})

    try:
        params['content'] = form.cleaned_data['content']
    except:
        params['content'] = ""
        errors.append({ "field": "content", "msg" :"Le premier message du sujet ne peut pas être vide"})

    try:
        params['author'] = User.objects.get(pk=request.user.id)
    except:
        errors.append({ "field": "visibdata", "msg" :"Auteur inconnu"})

    if params['visibility'] not in ["private", "class", "public"]:
        errors.append({ "field": "visibility", "msg" :"Type de visibilité invalide"})

    if params['visibdata'] != "":
        if params['visibility'] == "private":
            try:
                params['recipient'] = User.objects.get(pk=params['visibdata'])
            except:
                errors.append({ "field": "visibdata", "msg" :"Destinataire inconnu"})

        if params['visibility'] == "class":
            try:
                params['lesson'] = Lesson.objects.get(pk=params['visibdata'])
            except:
                errors.append({ "field": "visibdata", "msg" :"Classe inconnue"})

        if params['visibility'] == "public":
            try:
                params['professor'] =  Professor.objects.get(pk=params['visibdata'])
            except:
                errors.append({ "field": "visibdata", "msg" :"Professeur inconnu"})

    if params['skills'] != "":
        try:
            params['fetched_skills'] = Skill.objects.filter(pk__in=params['skills'].encode('utf8').split(" "))
            params['skills_fetched'] = True
        except:
            errors.append({ "field": "skills", "msg" :"Compétence(s) inconnue(s) ou mal formée(s) (format: id1 id2 ...)"})

    return params


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

    return render(request, "forum/thread.haml", {
        "user": request.user,
        "thread": thread,
        "messages": messages
    })


def reply_thread(request, id):
    """
    message_id = request.GET.get('message_id')

    content = ""  # TODO: access content

    thread = get_object_or_404(Thread, pk=id)
    message = Message(content=content, thread=thread)
    if message_id:
        parent_message = get_object_or_404(Message, pk=message_id)
        message.parent_message = parent_message
    """

    return HttpResponse()
