# Imports
from django.conf.urls import patterns, url

from locations import views


# Patters
urlpatterns = patterns('',
	# Locations
    url(r'^$', views.index),
    url(r'^map/$', views.map, name='map'),
)