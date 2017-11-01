from django.template.loader_tags import register


@register.inclusion_tag('forum/message.haml')
def message_partial(message, user, level=0):
    return {
        "message": message,
        "level": level + 1,
        "user": user
    }


@register.filter
def reply_margin(level):
    return (level - 1) * 20


@register.filter
def can_edit(user, message):
    return message.author == user
