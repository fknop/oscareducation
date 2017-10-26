# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST, require_GET

# Create your views here.
from forum.models import Thread, Message
from skills.models import Skill


class ThreadForm(forms.Form):
    title = forms.TextInput()
    skills = forms.MultipleChoiceField(queryset=Skill.objects.all())
    content = forms.Textarea()
    visibility = forms.ChoiceField()


@require_GET
def forum_dashboard(request):
    pass


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
    pass


def post_create_thread(request):
    form = ThreadForm(request.POST)

    if form.is_valid():
        title = form.cleaned_data['title']
        skills = form.cleaned_data['skills']
        content = form.cleaned_data['content']

        with transaction.atomic():
            thread = Thread(title=title, skills=skills)
            # TODO: set visibility
            thread.save()
            original_message = Message(content=content, parent_thread=thread)
            original_message.save()

    pass


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
    pass


def reply_thread(request, id):
    message_id = request.GET.get('message_id')

    content = ""  # TODO: access content

    thread = get_object_or_404(Thread, pk=id)
    message = Message(content=content, thread=thread)
    if message_id:
        parent_message = get_object_or_404(Message, pk=message_id)
        message.parent_message = parent_message

    return HttpResponse()
