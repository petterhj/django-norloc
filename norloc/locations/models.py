# Imports
from django.db import models
from django.db.models import Count


# Model: Point
class Point(models.Model):
    # Fields
    latitude = models.FloatField()
    longitude = models.FloatField()

    # Representation
    def __unicode__(self):
	   return '%s,%s' % (self.latitude, self.longitude)


# Model: Photo
class Photo(models.Model):
    # Fields
    photo = models.ImageField()
    title = models.CharField(max_length=100)
    credit = models.CharField(max_length=50)
    license = models.CharField(max_length=50, blank=True)

    # Representation
    def __unicode__(self):
        return self.title


# QuerySet: Locations
class LocationsQuerySet(models.QuerySet):
    def has_scene(self):
        # print self.
        # print self.aggregate(Count('productions.Scene'))
        # return self.annotate(scene_count=Count('productions.Scene')).filter(scene_count__isnull=False)
        # print [l for l in self.all() if l.scene_set.count() not 0]

        return self.all()


# Model: Location
class Location(models.Model):
    # Fields
    address = models.CharField(max_length=150)
    municipality = models.CharField(max_length=30)
    county = models.CharField(max_length=30)
    description = models.TextField(max_length=800, blank=True)
    bounds = models.ManyToManyField(Point)
    photos = models.ManyToManyField(Photo, blank=True)

    # Manager
    locations = LocationsQuerySet.as_manager()

    # Representation
    def __unicode__(self):
        return self.address
