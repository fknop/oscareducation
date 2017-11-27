# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime


class Thread(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, related_name="thread_author")
    title = models.CharField(max_length=255)
    skills = models.ManyToManyField("skills.Skill", blank=True)
    resource = models.ForeignKey("resources.Resource", null=True, blank=True, related_name="thread_resource")
    section = models.ForeignKey("skills.Section", blank=True, null=True)

    recipient = models.ForeignKey(User, null=True, related_name="thread_recipient")
    professor = models.ForeignKey("users.Professor", null=True)
    lesson = models.ForeignKey("promotions.Lesson", null=True)

    def is_private(self):
        return self.recipient is not None

    def is_public_lesson(self):
        return self.lesson is not None

    def is_public_professor(self):
        return self.professor is not None

    def messages(self):
        return Message.objects.select_related('author').filter(thread=self, parent_message=None).order_by(
            "created_date")

    def clean(self):
        super(Thread, self).clean()

        if self.is_public_professor() and not self.is_private() and not self.is_public_lesson():
            return True

        if not self.is_public_professor() and self.is_private() and not self.is_public_lesson():
            return True

        if not self.is_public_professor() and not self.is_private() and self.is_public_lesson():
            return True

        raise ValidationError('Thread: must be only one visibility')

    def get_absolute_url(self):
        return "/forum/thread/{}".format(self.id)

def directory_path(attachment, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'forum/{}/{}/{}'.format(attachment.message.thread.id, attachment.message.id, filename)

class MessageAttachment(models.Model):
    name = models.CharField(max_length=255)  # The name of the uploaded file
    file = models.FileField(upload_to=directory_path)
    message = models.ForeignKey("Message")



class Message(models.Model):
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()

    author = models.ForeignKey(User, related_name="message_author")
    thread = models.ForeignKey("Thread")
    parent_message = models.ForeignKey("self", null=True)

    content = models.TextField()

    class Meta:
        ordering = ['created_date']

    def get_absolute_url(self):
        return "/forum/thread/{}#message-{}".format(self.thread_id, self.id)

    def attachments(self):
        return MessageAttachment.objects.filter(message=self.id)

    def replies(self, include_self=False):
        replies = []
        if include_self:
            replies.append(self)

        for message in Message.objects.filter(thread=self.thread, parent_message=self).order_by('created_date'):
            replies.append(message)

        return replies


class LastThreadVisit(models.Model):
    last_visit = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    thread = models.ForeignKey('Thread')

    class Meta:
        unique_together = ("user", "thread")

    def update(self):
        self.last_visit = datetime.now()
