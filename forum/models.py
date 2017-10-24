# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Thread(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    private = models.BooleanField(default=True)

    skills = models.ManyToManyField("skills.Skill", blank=True)

    def messages(self):
        return Message.objects.filter(thread=self).order_by("created_date")


class Message(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    thread = models.ForeignKey(Thread)
    parent_message = models.ForeignKey("self", null=True)

    content = models.TextField()

    # attachments = models.ManyToManyField() TODO

    def replies(self):
        replies = []
        for message in Message.objects.filter(parent_message=self):
            replies.append(message)

        return replies

    def all_replies(self):
        replies = {self: []}
        for message in Message.objects.filter(parent_message=self).order_by("created_date"):
            replies[self].append(message.all_replies())

        return replies
