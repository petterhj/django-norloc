# Imports
from django.contrib import admin

from locations.models import Location, Point, Photo


# Models
admin.site.register(Location)
admin.site.register(Point)
admin.site.register(Photo)

'''
# ModelAdmin: Location
class LocationAdmin(admin.ModelAdmin):
    # List
    list_display = ('address', 'municipality', 'county')


# ModelAdmin: Point
class PointAdmin(admin.ModelAdmin):
    # List
    list_display = ('point', 'scene_point', 'location_point')

    def point(self, obj):
        return str(obj.latitude) + ', ' + str(obj.longitude)

    def scene_point(self, obj):
        return ' | '.join([s.scene.production.title + ': ' + s.scene.location.address for s in obj.shot_set.all()])

    scene_point.short_description = 'Scene point'

    def location_point(self, obj):
        return ' | '.join([l.address for l in obj.location_set.all()])

    location_point.short_description = 'Location bounds'


# ModelAdmin: Photo
class PhotoAdmin(admin.ModelAdmin):
    # List
    list_display = ('title', 'credit', 'license')


# Admin interface
admin.site.register(Location, LocationAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(Photo, PhotoAdmin)
'''