# -*- coding: utf-8 -*-
import json
import pickle
from __future__ import unicode_literals

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

    persistNotif(notification)

    if MSG_MEDIUM["WS"] in notification["medium"]
        sendWSNotif(notification)

def persistNotif(notification):

    serializedAudience = ""

    for a in notification["audience"]
        serializedAudience += a + " "

    Notification(
        audience=serializedAudience,
        medium=notification["medium"],
        notif_type=notification["type"],
        params = pickle.dumps(notification["params"])
    ).save()
