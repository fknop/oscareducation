from django.template.loader_tags import register


@register.inclusion_tag('forum/message.haml')
def message_partial(message, user, reply_to, level=0):
    return {
        "message": message,
        "reply_to": reply_to,
        "level": level + 1,
        "user": user
    }


@register.inclusion_tag('forum/leave_comment.haml')
def leave_comment_partial(title='', visibdata='', resource='', visibility=''):
    return {
        "title": title,
        "visibdata": visibdata,
        "resource": resource,
        "visibility": visibility
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
    return str(message.id) == reply_to


@register.filter
def is_selected_multiple(obj, selected):
    is_selected = len(selected) > 0 and any(obj.id == id for id in selected)
    return is_selected


@register.filter
def is_selected_single(obj_id, selected_id):
    if selected_id is not None:
        return obj_id == selected_id
    else:
        return False
