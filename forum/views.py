# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST, require_GET

# Create your views here.
from forum.models import Thread, Message
from dashboard import get_thread_set


class ThreadForm(forms.Form):
    title = forms.TextInput()
    content = forms.Textarea()
    visibility = forms.ChoiceField()

class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)



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
    return HttpResponse()


def post_create_thread(request):
    """
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
    """

    return HttpResponse()


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
    message_id = request.GET.get('message_id')
    thread = get_object_or_404(Thread, pk=id)
    form = MessageReplyForm(request.POST) # request.Post contains the data we want
    author = User.objects.get(pk=request.user.id)
    if form.is_valid():
        content = form.cleaned_data['content']
        message = Message.objects.create(content=content, thread=thread, author=author)
        message.save()

    return redirect(thread)

