from django.conf.urls import url
from django.views.generic import TemplateView


from . import ajax

# These urls are prefixed by notfication/
urlpatterns = [
    url(r'^last/$', ajax.getLastNotifications, name='getLastNotifications'),
    url(r'^seen/$', ajax.setNotificationAsSeen, name='setNotificationAsSeen'),
]
