# In consumers.py
from channels import Channel, Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http
from from users.models import Student, Professor

@channel_session_user_from_http
def ws_add(message):
    message.reply_channel.send({"accept": True})
    Group("notification-user-%s" % message.user.id).add(message.reply_channel)
    Group("notification-user-all").add(message.reply_channel)
    addUserInItsClassGroups(message)

def addUserInItsClassGroups(message):

    try
        for lesson in Student.objects.get(pk=message.user.id).lesson_set.all()
            Group("notification-class-%s" % lesson.id).add(message.reply_channel)
    except
        pass

    try
        for lesson in Professor.objects.get(pk=message.user.id).lesson_set.all()
            Group("notification-class-%s" % lesson.id).add(message.reply_channel)
    except
        pass

@channel_session_user
def ws_message(message):
    Group("notification-user-%s" % message.user.id).send({
        "text": str(message.user.id),
    })

@channel_session_user
def ws_disconnect(message):
    Group("notification-user-%s" % message.user.id).discard(message.reply_channel)
