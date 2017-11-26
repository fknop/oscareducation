# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    audience = models.TextField()
    medium = models.CharField(max_length=255)
    notif_type = models.CharField(max_length=255)
    params = models.TextField()
    seen = models.TextField(default="")
