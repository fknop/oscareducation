# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from channels import Group
from notification.notif_types import NOTIF_TYPES

# for @param notification structure check in 'notification/notification_manager.py'
def sendWSNotif(notification):

    for group in notification["audience"]:
        WSMsg = {
            "text": json.dumps({
                "type": notification["type"],
                "params": notification["params"],
                "created_date": notification["created_date"],
                "server_group": group,
                "notif_id": notification["notif_id"],
                "seen": notification["seen"]
            })
        }
        Group(group).send(WSMsg)
