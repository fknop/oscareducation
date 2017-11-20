# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from channels import Group
from notification.notif_types import NOTIF_TYPES

# for @param notification structure check in 'notification/notification_manager.py'
def sendWSNotif(notification):

    WSMsg = {
        "text": json.dumps({
            "type": notification["type"],
            "params": notification["params"],
        })
    }

    for group in notification["audience"]:
        Group(group).send(WSMsg)
