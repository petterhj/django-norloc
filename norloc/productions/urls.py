# Imports
from django.conf.urls import patterns, url

from productions import views


# Patters
urlpatterns = patterns('',
	# Productions
    url(r'^$', views.index, name='productions'),
    url(r'^films/$', views.index, {'filter_type': 'films'}, name='films'),
    url(r'^series/$', views.index, {'filter_type': 'series'}, name='series'),

    # Production
    url(r'^production/(?P<slug>[\w-]+)/$', views.production, name='production'),
    url(r'^production/(?P<slug>[\w-]+)/scene/(?P<scene_id>\d+)/locator/$', views.locator, name='locator'),

)