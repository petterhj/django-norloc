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

    # url(r'^produksjoner/$', include([
    #     url(r'^$', prd.productions, name='productions')
    # ])),

    url(r'^produksjoner/$', prd.productions, name='productions'),
    url(r'^produksjoner/import/$', prd.import_production, name='import_production'),
    url(r'^produksjoner/import/(?P<production_type>film|tv)/(?P<tmdb_id>\d+)$', prd.import_production, name='import_production'),
    url(r'^produksjoner/(?P<filter>[\w-]+)/$', prd.productions, name='filtered_productions'),
    url(r'^produksjoner/(?P<production_type>film|tv)/(?P<slug>[\w-]+)/$', prd.production, name='production'),

    url(r'^folk/$', prd.people, name='people'),
    url(r'^folk/import/$', prd.import_person, name='import_person'),
    url(r'^folk/(?P<filter>[\w-]+)/$', prd.people, name='filtered_people'),
    url(r'^person/(?P<slug>[\w-]+)/$', prd.person, name='person'),
    
    url(r'^kart/$', prd.map, name='map'),

    url(r'^json/production/(?P<ppk>\d+)/locations/$', prd.locations, name='production_locations'),
    url(r'^json/shots/$', prd.shots, name='shots'),
    url(r'^json/scenes/$', prd.scenes, name='scenes'),
    url(r'^json/tags/people/$', prd.people_tags, name='people_tags'),
    url(r'^json/tags/companies/$', prd.companies_tags, name='companies_tags'),
    url(r'^json/tmdb/production/search/$', prd.tmdb_production_search, name='tmdb_production_search'),
    url(r'^json/tmdb/production/(?P<production_type>film|tv)/details/(?P<tmdb_id>\d+)$', prd.tmdb_production_details, name='tmdb_production_details'),
    url(r'^json/tmdb/people/search/$', prd.tmdb_people_search, name='tmdb_people_search'),
    url(r'^json/tmdb/people/details/(?P<tmdb_id>\d+)$', prd.tmdb_person_details, name='tmdb_person_details'),

    url(r'^opptakssteder/$', loc.locations, name='locations'),
    url(r'^opptakssteder/(?P<filter>[\w-]+)/$', loc.locations, name='filtered_locations'),
    url(r'^json/locations/$', loc.locations, {'json': 'True'}, name='json_locations'),

    url(r'^json/location/(?P<lpk>\d+)/details$', loc.location_details, name='location_details'),
    url(r'^json/location/(?P<lpk>\d+)/bounds/update$', loc.update_location_bounds, name='update_bounds'),
    # url(r'^json/locations/$', loc.locations, name='locations'),

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

