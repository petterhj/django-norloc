# -*- coding: utf-8 -*-

# Imports
from django.db import models
from django.db.models import Count
from autoslug import AutoSlugField
from jsonfield import JSONField
from uuid_upload_path import upload_to_factory


# # QuerySet: Locations
# class LocationsQuerySet(models.QuerySet):
#     def has_scene(self):
#         # print self.
#         # print self.aggregate(Count('productions.Scene'))
#         # return self.annotate(scene_count=Count('productions.Scene')).filter(scene_count__isnull=False)
#         # print [l for l in self.all() if l.scene_set.count() not 0]

#         return self.all()


# Upload factories
MIGRATE = False
upload_to_photos = upload_to_factory('locations') if not MIGRATE else 'locations'


NO_COUNTIES = (
    ('akershus', 'Akershus'), ('austagder', 'Aust-Agder'), ('buskerud', 'Buskerud'), 
    ('finnmark', 'Finnmark'), ('hedmark', 'Hedmark'), ('hordaland', 'Hordaland'), 
    ('jan-mayen', 'Jan Mayen'), ('more-og-romsdal', 'Møre og Romsdal'), 
    ('nordtrondelag', 'Nord-Trøndelag'), ('nordland', 'Nordland'), ('oppland', 'Oppland'), 
    ('oslo', 'Oslo'), ('rogaland', 'Rogaland'), ('sogn-og-fjordane', 'Sogn og Fjordane'), 
    ('svalbard', 'Svalbard'), ('sortrondelag', 'Sør-Trøndelag'), ('telemark', 'Telemark'), 
    ('troms', 'Troms'), ('vestagder', 'Vest-Agder'), ('vestfold', 'Vestfold'), 
    ('ostfold', 'Østfold')
)

LOCATION_TYPES = (
    ('park', 'Park'), ('street', 'Gate'),
)


# Model: Location
class Location(models.Model):
    # Fields
    address = models.CharField(max_length=150)
    place = models.CharField(max_length=30)
    county = models.CharField(max_length=20, choices=NO_COUNTIES)
    description = models.TextField(max_length=800, blank=True)
    description_credit = models.CharField(max_length=50, blank=True)
    location_type = models.CharField(max_length=30, choices=LOCATION_TYPES, blank=True)
    bounds = JSONField(blank=True, null=True)
    bounds_locked = models.BooleanField(default=False)

    place_slug = AutoSlugField(**{
        'populate_from': 'place', 
        # 'unique_with': ('county',), 
        'unique': False,
        'editable': True,
        'always_update': True,
        'null': True,
    })
    slug = AutoSlugField(**{
        'populate_from': 'address', 
        'unique_with': ('county', 'place_slug'), 
        'editable': True
    })

    # Manager
    # locations = LocationsQuerySet.as_manager()

    # Metadata
    class Meta:
        ordering = ['address']


    # Properties
    @property
    def full_address(self):
        return ', '.join([self.address, self.place, self.get_county_display()])

    # @property
    # def production_count(self):
    #     return self.scene_set.count()

    @property
    def photo(self):
        photo = self.photo_set.first()
        return photo.photo if photo and photo.photo else None
    
    
    # Representation
    def __unicode__(self):
        return self.address


# Model: Photo
class Photo(models.Model):
    # Fields
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=upload_to_photos)
    title = models.CharField(max_length=100)
    credit = models.CharField(max_length=50)
    license = models.CharField(max_length=50, blank=True)

    # Representation
    def __unicode__(self):
        return self.title