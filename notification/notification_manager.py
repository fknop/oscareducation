# -*- coding: utf-8 -*-
import json
from __future__ import unicode_literals

from .models import Notification
from .notif_types import NOTIF_TYPES
from .ws_notification import sendWSNotif

NOTIF_MEDIUM = {
    "WS": "ws",  # Web Sockets
#   "EMAIL": "email"
}

# @param notification structure:
#
# {
#    "medium": notification_manager.NOTIF_MEDIUM,
#
#    "type": notif_types.NOTIF_TYPES,
#
#    // recipient of notif, depends on medium; per ex for WS, list of groups
#    "audience": [...],
#
#    // data relatives to notification type, depends on notif type;
#    // per ex for NEW_PRIVATE_FORUM_THREAD: { "author": int }
#    "params": {...},
# }
#
# all fields are required.
def sendNotification(notification):

    persistNotif(notification)

    if MSG_MEDIUM["WS"] in notification["medium"]
        sendWSNotif(notification)

#def persistNotif(notification):

#    if notification["type"] == MSG_TYPES["NEW_PUBLIC_FORUM_THREAD"]:

#    elif notification["type"] == MSG_TYPES["NEW_PUBLIC_FORUM_MESSAGE"]:

#    elif notification["type"] == MSG_TYPES["NEW_PUBLIC_FORUM_THREAD"]:

#    elif notification["type"] == MSG_TYPES["NEW_PRIVATE_FORUM_THREAD"]:

#    elif notification["type"] == MSG_TYPES["NEW_PRIVATE_FORUM_MESSAGE"]:

#    elif notification["type"] == MSG_TYPES["NEW_class_FORUM_THREAD"]:

#    elif notification["type"] == MSG_TYPES["NEW_class_FORUM_MESSAGE"]:
