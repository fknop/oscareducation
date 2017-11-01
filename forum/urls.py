from django.conf.urls import url
from django.views.generic import TemplateView


from . import views


# These urls are prefixed by forum/
urlpatterns = [
    url(r'^$', views.forum_dashboard, name='forum_dashboard'),
    url(r'^write/', views.create_thread, name='forum_write'),
    url(r'^thread/(?P<id>\d+)', views.thread, name='view_thread')
]


