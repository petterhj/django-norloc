# Imports
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from productions import views as prd
from locations import views as loc


# URL patterns
urlpatterns = [
    url(r'^$', prd.index, name='index'),

    url(r'^map/$', prd.map, name='map'),

    url(r'^production/(?P<slug>[\w-]+)/$', prd.production, name='production'),
    url(r'^people/(?P<slug>[\w-]+)/$', prd.person, name='person'),

    url(r'^productions/import/$', prd.import_production, name='import_production'),

    url(r'^json/production/(?P<ppk>\d+)/locations/$', prd.locations, name='production_locations'),
    url(r'^json/shots/$', prd.shots, name='shots'),
    url(r'^json/scenes/$', prd.scenes, name='scenes'),
    url(r'^json/tmdb/search/$', prd.tmdb_search, name='tmdb_search'),
    url(r'^json/tmdb/details/(?P<tmdb_id>\d+)$', prd.tmdb_details, name='tmdb_details'),

    url(r'^json/location/(?P<lpk>\d+)/details$', loc.location_details, name='location_details'),
    url(r'^json/location/(?P<lpk>\d+)/bounds/update$', loc.update_location_bounds, name='update_bounds'),
    url(r'^json/locations/$', loc.locations, name='locations'),

    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





'''
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib import admin

import views

admin.autodiscover()

urlpatterns = patterns('',
    # Main
    url(r'^$', views.index),

    # Apps
    url(r'^productions/', include('productions.urls')),
    url(r'^locations/', include('locations.urls')),

    # Test
    url(r'^test/', TemplateView.as_view(template_name='test.html')),

    # Tooltips
    url(r'^tooltip/login', TemplateView.as_view(template_name='tooltip_login.html')),
    url(r'^tooltip/user', TemplateView.as_view(template_name='tooltip_user.html')),

    # Auth
    url(r'^login/', views.login),
    url(r'^logout/', views.logout),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Productions
    url(r'^$', views.index, name='productions'),
    url(r'^films/$', views.index, {'filter_type': 'films'}, name='films'),
    url(r'^series/$', views.index, {'filter_type': 'series'}, name='series'),

    # Production
    url(r'^production/(?P<slug>[\w-]+)/$', views.production, name='production'),
    url(r'^production/(?P<slug>[\w-]+)/scene/(?P<scene_id>\d+)/locator/$', views.locator, name='locator'),

'''

