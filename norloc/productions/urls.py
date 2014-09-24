# Imports
from django.conf.urls import patterns, url

from productions import views


# Patters
urlpatterns = patterns('',
	# Productions
    url(r'^$', views.index),
    url(r'^films/$', views.index, {'type': 'films'}),
    url(r'^series/$', views.index, {'type': 'series'}),

    # Production
    url(r'^production/(?P<slug>[\w-]+)/$', views.production, name='production'),

)