from django.conf.urls import url
from django.views.generic import TemplateView

from utils import user_is_student

from . import views

urlpatterns = [
    url(r'^forum/', views.forum_dashboard, name='forum_dashboard'),
    url(r'^forum/write', views.create_thread, name='forum_write'),
    url(r'^forum/thread/(?P<id>\d+)', views.thread, name='view_thread'),
]


