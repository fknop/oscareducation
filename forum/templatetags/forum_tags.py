from django.template.loader_tags import register
from ..views import can_update as views_can_update

@register.inclusion_tag('forum/message.haml')
def message_partial(message, user, reply_to, last_visit, edit, level=0):
    return {
        "last_visit": last_visit,
        "message": message,
        "reply_to": reply_to,
        "level": level + 1,
        "user": user,
        "edit": edit
    }


@register.inclusion_tag('forum/leave_comment.haml')
def leave_comment_partial(title='', visibdata='', resource='', visibility='', skill='', section=''):
    """
    Renders the template which creates a clickable icon. It redirects to the forum's creation page with some
    fields prefilled depending on the parameters. All parameters are strings.
    :param title: The title of the thread
    :param visibdata: The id of the recipient
    :param resource:  The id of the related resource
    :param visibility: The visibility of the thread (private|class|public)
    :param skill: The id of the related skill
    :param section: The id of the related section
    :return: The rendered template with a working link
    """
    return {
        "title": title,
        "visibdata": visibdata,
        "resource": resource,
        "visibility": visibility,
        "skill": skill,
        "section": section
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
def is_selected_multiple(obj, selected):
    """
    Returns True if the id of the object is in the list of given ids, False otherwise.
    :param obj: the object with an id property
    :param selected: a list of ids
    :return: True or False
    """
    is_selected = len(selected) > 0 and any(obj.id == id for id in selected)
    return is_selected


@register.filter
def is_selected_single(obj_id, selected_id):
    """
    Returns True if the the ids are equal and not None.
    :param obj_id: the id of the object
    :param selected_id: another id
    :return: True or False
    """
    if selected_id is not None:
        return obj_id == selected_id
    else:
        return False
