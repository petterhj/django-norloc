# Imports
from django.contrib import admin

from locations.models import Location, Photo



# ModelAdmin: Location
class LocationAdmin(admin.ModelAdmin):
    # List
    list_display = (
        'address', 'slug', 'place', 'place_slug', 'county',
        'location_type'
    )


# ModelAdmin: Photo
class PhotoAdmin(admin.ModelAdmin):
    # List
    list_display = ('location', 'title', 'credit', 'license')


# Models
admin.site.register(Location, LocationAdmin)
admin.site.register(Photo, PhotoAdmin)
