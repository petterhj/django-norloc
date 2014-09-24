# Imports
from django.conf.urls import patterns, url

from locations import views


# Patters
urlpatterns = patterns('',
    url(r'^$', views.index)
)