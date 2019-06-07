# Imports
from django.contrib import admin
from urllib.parse import urlparse

from locations.models import Location, Photo



# ModelAdmin: Location
class LocationAdmin(admin.ModelAdmin):
    # List
    list_display = (
        'address', 'slug', 'place', 'place_slug', 'county',
        'location_type', 'list_has_bounds',
    )

    # Has bounds
    def list_has_bounds(self, obj):
        return obj.has_bounds
    list_has_bounds.boolean = True
    list_has_bounds.short_description = 'Bounds'



# ModelAdmin: Photo
class PhotoAdmin(admin.ModelAdmin):
    # List
    list_display = ('location', 'title', 'credit', 'list_source', 'license')

	# Source
    def list_source(self, obj):
        return urlparse(obj.source).hostname.replace('www.', '') if obj.source else ''
    list_source.short_description = 'Source'



# Models
admin.site.register(Location, LocationAdmin)
admin.site.register(Photo, PhotoAdmin)
