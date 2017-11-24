from django.template.loader_tags import register
from ..views import can_update as views_can_update

@register.inclusion_tag('forum/message.haml')
def message_partial(message, user, reply_to, edit, level=0):
    return {
        "message": message,
        "reply_to": reply_to,
        "level": level + 1,
        "user": user,
        "edit": edit
    }


@register.inclusion_tag('forum/reply_form.haml')
def reply_form_partial(message):
    return {
        "message": message
    }


@register.filter
def reply_margin(level):
    return (min([level, 4]) - 1) * 20

@register.filter
def is_editing(message, edit):
    print(message.id, edit)
    return message.id == edit

@register.filter
def can_update(user, message):
    return views_can_update(message.thread, message, user)

@register.filter
def is_reply_to(reply_to, message):
    return str(message.id) == reply_to

@register.filter
def is_section_selected(section, selected):
    if selected is not None:
        return section.id == selected
    else:
        return False

@register.filter
def is_skill_selected(skill, selected):
    is_selected = len(selected) > 0 and any(skill.id == id for id in selected)
    return is_selected
