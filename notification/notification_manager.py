# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from notification.models import Notification
from .notif_types import NOTIF_TYPES
from .web_sockets.ws_notification import sendWSNotif

NOTIF_MEDIUM = {
    "WS": "ws",  # Web Sockets
                 # Add other types for instance: "EMAIL": "email"
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
#    // per ex for NEW_PRIVATE_FORUM_THREAD: { "thread": Thread }
#    "params": {...},
# }
#
# all fields are required.
def sendNotification(notification):

    persistedNotif = persistNotif(notification)

    if notification["medium"] == NOTIF_MEDIUM["WS"]:
        sendWSNotif(notification)

def persistNotif(notification):

    serializedAudience = " "

    for a in notification["audience"]:
        serializedAudience += (a + " ")

    notif = Notification(
        audience=serializedAudience,
        medium=notification["medium"],
        notif_type=notification["type"],
        params = json.dumps(notification["params"]),
        seen=""
    )

    notif.save()

    notification['created_date'] = {
        "day": notif.created_date.day,
        "month": notif.created_date.month,
        "year": notif.created_date.year,
        "hour": notif.created_date.hour,
        "minute": notif.created_date.minute,
        "second": notif.created_date.second
    }

    notification['notif_id'] = notif.id
    notification['seen'] = notif.seen

    return notif
