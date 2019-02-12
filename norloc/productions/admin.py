# Imports
from django.contrib import admin

from productions.models import Production, Person, Company, Scene, Shot


# ModelAdmin: Production
class ProductionAdmin(admin.ModelAdmin):
    # List
    list_display = ('poster_thumb', 'title', 'slug', 'type', 'release', 'runtime')
    list_display_links = ('poster_thumb', 'title',)

    def poster_thumb(self, obj):
        if not obj.poster:
            return 'NOP'
        return '<img src="' + obj.poster.url + '" alt="thumb" style="margin: -4px -5px -5px 0; height: 22px;" />'

    poster_thumb.short_description = 'Poster'
    poster_thumb.allow_tags = True

    # Fieldsets
    fieldsets = [
        ('Production', {
            'fields': [
                'type', 'title', 'slug', 'release', 'summary', 'summary_credit', 
                'directors', 'writers', 'photographers',
                'runtime', 'producers', 'distributors'
            ]
        }),
        ('Images', {
            'fields': ['poster', 'backdrop']
        }),
        ('External information', {
            'fields': ['imdb_id', 'tmdb_id', 'nbdb_id', 'tvdb_id']
        }),
    ]


# ModelAdmin: Scene
class SceneAdmin(admin.ModelAdmin):
    # List
    list_display = ('production', 'location')

    # Fieldsets
    fieldsets = [
        ('Scene', {'fields': ['production', 'description']}),
        ('Location', {'fields': ['location', 'uncertain']}),
    ]

    #def point_link(self, obj):
    #    return '<a href="http://maps.google.com/maps?&z=15&q=%s" target="_blank">%s</a>' % (obj.point, obj.point) if obj.point else '(None)'

    #point_link.allow_tags = True
    #point_link.short_description = 'Point'


# ModelAdmin: Shot
class ShotAdmin(admin.ModelAdmin):
    # List
    list_display = ('shot_thumb', 'shot_production', 'shot_location', 'timecode', 'coordinate')

    def shot_thumb(self, obj):
        return '<img src="' + obj.image.url + '" alt="thumb" style="margin: -4px -5px -5px 0; width: 39px; height: 22px;" />'
        # return 'test'

    def shot_production(self, obj):
        return obj.scene.production.title

    def shot_location(self, obj):
        if obj.scene.location:
            return obj.scene.location.address
        return None

    def coordinate(self, obj):
        if obj.latitude and obj.longitude:
            return '<a href="http://www.google.com/maps/place/%s,%s" target="_blank">%s,%s</a>' % (
                str(obj.latitude), str(obj.longitude),
                str(obj.latitude), str(obj.longitude),
            )
        return None

    shot_thumb.short_description = 'Shot'
    shot_thumb.allow_tags = True
    shot_production.short_description = 'Production'
    shot_production.admin_order_field = 'scene__production__title'
    shot_location.short_description = 'Location'
    shot_location.admin_order_field = 'scene__location__address'
    coordinate.allow_tags = True


# ModelAdmin: Person
class PersonAdmin(admin.ModelAdmin):
    # List
    list_display = ('headshot_thumb', 'name', 'slug', 'tmdb_id', 'imdb_id')
    list_display_links = ('name',)

    def headshot_thumb(self, obj):
        if not obj.headshot:
            return ''
        return '<img src="' + obj.headshot.url + '" alt="thumb" style="margin: -4px -5px -5px 0; height: 22px; border-radius: 50%;" />'

    headshot_thumb.short_description = 'Poster'
    headshot_thumb.allow_tags = True


# ModelAdmin: Company
class CompanyAdmin(admin.ModelAdmin):
    # List
    list_display = ('name', 'website')


# Models
admin.site.register(Production, ProductionAdmin)
admin.site.register(Scene, SceneAdmin)
admin.site.register(Shot, ShotAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Company, CompanyAdmin)