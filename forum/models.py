# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Thread(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, related_name="message_author")
    title = models.CharField(max_length=255)

    skills = models.ManyToManyField("skills.Skill", blank=True)

    recipient = models.ForeignKey(User, null=True, related_name="message_recipient")
    professor = models.ForeignKey("users.Professor", null=True)
    lesson = models.ForeignKey("promotions.Lesson", null=True)

    def is_private(self):
        return self.recipient is not None

    def is_public_lesson(self):
        return self.lesson is not None

    def is_public_professor(self):
        return self.professor is not None

    def messages(self):
        return Message.objects.filter(thread=self).order_by("created_date")

    def clean(self):
        super(Thread, self).clean()

        if self.is_public_professor() and not self.is_private() and not self.is_public_professor():
            return True

        if not self.is_public_professor() and self.is_private() and not self.is_public_professor():
            return True

        if not self.is_public_professor() and not self.is_private() and self.is_public_professor():
            return True

        return False


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
