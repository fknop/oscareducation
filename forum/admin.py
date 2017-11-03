# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Thread, MessageAttachment, Message
# Register your models here.

admin.site.register(Thread)
admin.site.register(Message)
admin.site.register(MessageAttachment)