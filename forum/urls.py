from django.conf.urls import url
from django.views.generic import TemplateView


from . import views


# These urls are prefixed by forum/
urlpatterns = [
    url(r'^$', views.forum_dashboard, name='forum_dashboard'),
    url(r'^write/$', views.create_thread, name='forum_write'),
    url(r'^write/users$', views.get_users, name='get_users'),
    url(r'^write/professors$', views.get_professors, name='get_professors'),
    url(r'^write/lessons$', views.get_lessons, name='get_lessons'),
    url(r'^thread/(?P<id>\d+)$', views.thread, name='view_thread'),
    url(r'^thread/(?P<id>\d+)/edit/(?P<message_id>\d+)$', views.edit_message, name='edit_message'),
    url(r'^thread/(?P<id>\d+)/delete/(?P<message_id>\d+)$', views.delete_message, name='delete_message')
]


