from django.template.loader_tags import register


@register.inclusion_tag('forum/message.haml')
def message_partial(message, user, reply_to, level=0):
    return {
        "message": message,
        "reply_to": reply_to,
        "level": level + 1,
        "user": user
    }


@register.inclusion_tag('forum/reply_form.haml')
def reply_form_partial():
    return {}


@register.filter
def reply_margin(level):
    return (min([level, 4]) - 1) * 20


@register.filter
def can_edit(user, message):
    return message.author == user

@register.filter
def is_reply_to(reply_to, message):
    print(reply_to, str(message.id))
    return str(message.id) == reply_to
