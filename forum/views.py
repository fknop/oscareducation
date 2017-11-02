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


@require_GET
def forum_dashboard(request):
    return HttpResponse()


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
    return render(request, "forum/new_thread.haml")

class ThreadForm(forms.Form):
    title = forms.CharField()
    visibdata = forms.CharField()
    skills = forms.CharField()
    content = forms.CharField()

def post_create_thread(request):

    form = ThreadForm(request.POST)

    if form.is_valid():

        title = form.cleaned_data['title']
        visibility = request.POST.get('visibility')
        visibdata = form.cleaned_data['visibdata']
        skills = form.cleaned_data['skills'].encode('utf8').split(" ")
        content = form.cleaned_data['content']
        author = User.objects.get(pk=request.user.id)

        with transaction.atomic():

            thread = Thread(title=title, author=author)

            if visibility == 'private':
                thread.recipient = User.objects.get(pk=visibdata)

            if visibility == 'class':
                thread.lesson = Lesson.objects.get(pk=visibdata)

            if visibility == 'public':
                thread.professor = Professor.objects.get(pk=visibdata)

            thread.save()
            thread.skills = Skill.objects.filter(pk__in=skills)
            thread.save()

            original_message = Message(content=content, thread=thread, author=author)
            original_message.save()

        return redirect('/forum/thread/' + str(thread.id))

    else:
        return redirect('/forum/write')


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
