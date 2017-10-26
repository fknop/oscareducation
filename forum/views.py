# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST


# Create your views here.

def forum_dashboard(request):
    pass

def write_thread(request):
    pass


@require_POST
def create_thread(request):
    pass


def view_thread(request, id):
    pass


@require_POST
def reply_thread(request, id):

    """
    message_id = request.GET.get('message_id')

    content = ""  # TODO: access content

    thread = get_object_or_404(Thread, pk=id)
    message = Message(content=content, thread=thread)
    if message_id:
        parent_message = get_object_or_404(Message, pk=message_id)
        message.parent_message = parent_message

    return HttpResponse()
    """

    pass