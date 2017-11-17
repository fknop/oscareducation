# -*- coding: utf-8 -*-
import json
from __future__ import unicode_literals

from .models import Notification

MSG_MEDIUM = {
    "WS": "WS"
}

MSG_TYPES = {
    "NEW_PUBLIC_FORUM_THREAD": "new_public_forum_thread",
    "NEW_PUBLIC_FORUM_MESSAGE": "new_public_forum_message",
    "NEW_PRIVATE_FORUM_THREAD": "new_private_forum_thread",
    "NEW_PRIVATE_FORUM_MESSAGE": "new_private_forum_message"
}

def sendNotification(user_to, notification):

    persistNotif(notification)

    if notification["type"] == MSG_TYPES["NEW_PUBLIC_FORUM_THREAD"]:

    elif notification["type"] == MSG_TYPES["NEW_PUBLIC_FORUM_MESSAGE"]:

    elif notification["type"] == MSG_TYPES["NEW_PUBLIC_FORUM_THREAD"]:

    elif notification["type"] == MSG_TYPES["NEW_PRIVATE_FORUM_THREAD"]:

    elif notification["type"] == MSG_TYPES["NEW_PRIVATE_FORUM_MESSAGE"]:

    if notification["medium"] == MSG_MEDIUM["WS"]
        Group("notification-user-%s" % user_to).send({
            "text": json.dumps({
                "type": notification["type"],
                "params": params,
                "redirectOnClick": notification["redirectOnClick"]
            })
        })

def persistNotif(notification):

    if notification["type"] == MSG_TYPES["NEW_PUBLIC_FORUM_THREAD"]:

    elif notification["type"] == MSG_TYPES["NEW_PUBLIC_FORUM_MESSAGE"]:

    elif notification["type"] == MSG_TYPES["NEW_PUBLIC_FORUM_THREAD"]:

    elif notification["type"] == MSG_TYPES["NEW_PRIVATE_FORUM_THREAD"]:

    elif notification["type"] == MSG_TYPES["NEW_PRIVATE_FORUM_MESSAGE"]:
