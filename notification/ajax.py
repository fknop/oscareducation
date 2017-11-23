# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from notification.models import Notification
from django.db.models import Q
from notification_manager import NOTIF_MEDIUM

def require_login(function):
    return login_required(function, login_url="/accounts/usernamelogin")

@require_POST
@require_login
def setNotificationAsSeen(request):

    try:
        raw_ids = json.loads(request.body)['notif_ids']
        notif_ids = []
        notifs = None

        for id in raw_ids:
            notif_ids.append(int(id))

        notifs = Notification.objects.filter(pk__in=notif_ids)

        for notif in notifs:
            if str(request.user.id) not in notif.seen:
                notif.seen += " " + str(request.user.id)
                notif.save()

        return HttpResponse(status=200)

    except:
        return HttpResponseServerError(
            "Error: malformed data, empty notif_ids set or unknown notif_ids")

@require_GET
@require_login
def getLastNotifications(request):

    notifications = []
    medium = request.GET.get('medium')
    qObjAudience = getNotificationQObjAudienceFor(request.user)

    notifQuerySet = Notification.objects.filter(
        qObjAudience & Q(medium=medium) ).order_by("-created_date")

    for fetchNotif in notifQuerySet:

        notif = {
            "type": fetchNotif.notif_type,
            "notif_id": fetchNotif.id,
            "params": json.loads(fetchNotif.params),
            "created_date": {
                "day": fetchNotif.created_date.day,
                "month": fetchNotif.created_date.month,
                "year": fetchNotif.created_date.year,
                "hour": fetchNotif.created_date.hour,
                "minute": fetchNotif.created_date.minute,
                "second": fetchNotif.created_date.second
            },
            "seen": fetchNotif.seen
        }

        if fetchNotif.medium == NOTIF_MEDIUM["WS"]:
            notif["server_group"] = inferServerGroup(request.user, fetchNotif)

        notifications.append(notif)

    return HttpResponse(json.dumps({ "notifs": notifications }), content_type="application/json")


def getNotificationQObjAudienceFor(user):

    qObj = Q(audience__contains=("notification-user-%s" % user.id))

    for lesson in getClassesOfUser(user):
        qObj |= Q(audience__contains=("notification-class-%s" % lesson.id))

    return qObj

def inferServerGroup(user, notif):

    userServerGroup = ("notification-user-%s" % user.id)
    serverGroup = None

    if userServerGroup in notif.audience:
        serverGroup = userServerGroup
    else:
        userClasses = getClassesOfUser(user)

        for c in userClasses:
            classServerGroup = ("notification-class-%s" % c.id)

            if classServerGroup in notif.audience:
                serverGroup = classServerGroup

    return serverGroup

def getClassesOfUser(user):

    userClasses = []

    try:
        for lesson in Student.objects.get(user=user).lesson_set.all():
            userClasses.append(lesson)
    except:
        pass

    try:
        for lesson in Professor.objects.get(user=user).lesson_set.all():
            userClasses.append(lesson)
    except:
        pass

    return userClasses
