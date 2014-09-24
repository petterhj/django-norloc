# Imports
from django.contrib import admin
from productions.models import Production, Scene, Shot, Director, Company


# ModelAdmin: Production
class ProductionAdmin(admin.ModelAdmin):
    # List
    list_display = ('title', 'slug', 'type', 'release')

    # Fieldsets
    fieldsets = [
        ('Production', {'fields': ['type', 'title', 'slug', 'release', 'summary', 'directors', 'runtime', 'producers', 'distributors']}),
        ('Images', {'fields': ['poster', 'backdrop']}),
        ('External information', {'fields': ['imdb_id', 'tmdb_id', 'nbdb_id', 'tvdb_id']}),
    ]


# ModelAdmin: Scene
class SceneAdmin(admin.ModelAdmin):
    # List
    list_display = ('production', 'location')

    # Fieldsets
    fieldsets = [
        ('Scene', {'fields': ['production', 'description']}),
        ('Location', {'fields': ['location']}),
    ]

    #def point_link(self, obj):
    #    return '<a href="http://maps.google.com/maps?&z=15&q=%s" target="_blank">%s</a>' % (obj.point, obj.point) if obj.point else '(None)'

    #point_link.allow_tags = True
    #point_link.short_description = 'Point'


# ModelAdmin: Shot
class ShotAdmin(admin.ModelAdmin):
    # List
    list_display = ('shot_thumb', 'shot_production', 'shot_location')

    def shot_thumb(self, obj):
        return '<img src="' + obj.image.url + '" alt="thumb" style="margin: -4px -5px -5px 0; width: 39px; height: 22px;" />'
        # return 'test'

    def shot_production(self, obj):
        return obj.scene.production.title

    def shot_location(self, obj):
        return obj.scene.location.address

    shot_thumb.short_description = 'Shot'
    shot_thumb.allow_tags = True
    shot_production.short_description = 'Production'
    shot_production.admin_order_field = 'scene__production__title'
    shot_location.short_description = 'Location'
    shot_location.admin_order_field = 'scene__location__address'


# Admin interface
admin.site.register(Production, ProductionAdmin)
admin.site.register(Scene, SceneAdmin)
admin.site.register(Shot, ShotAdmin)
admin.site.register(Director)
admin.site.register(Company)
# admin.site.register(Distributor)
