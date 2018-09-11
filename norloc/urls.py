# Imports
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from productions import views


# URL patterns
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^production/(?P<slug>[\w-]+)/$', views.production, name='production'),

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
'''