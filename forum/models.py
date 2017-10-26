# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Thread(models.Model):
    PRIVATE = 'PRI'
    PUBLIC_CLASS = 'PUC'
    PUBLIC_TEACHER = 'PUT'
    VISIBILITY_CHOICES = (
        (PRIVATE, 'Private'),
        (PUBLIC_CLASS, 'Public Class'),
        (PUBLIC_TEACHER, 'Public Teacher')
    )

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    visibility = models.CharField(max_length=3, default=PRIVATE, choices=VISIBILITY_CHOICES)

    skills = models.ManyToManyField("skills.Skill", blank=True)

    def is_private(self):
        return self.visibility == self.PRIVATE

    def is_public_class(self):
        return self.visibility == self.PUBLIC_CLASS

    def is_public_teacher(self):
        return self.visibility == self.PUBLIC_TEACHER

    def messages(self):
        return Message.objects.filter(thread=self).order_by("created_date")


class MessageAttachment(models.Model):
    name = models.CharField(max_length=255)  # The name of the uploaded file
    file = models.FileField()
    message = models.ForeignKey("Message")


class Message(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    thread = models.ForeignKey("Thread")
    parent_message = models.ForeignKey("self", null=True)

    content = models.TextField()

    def attachments(self):
        return MessageAttachment.objects.filter(message=self.id)

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
