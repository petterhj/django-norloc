# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals
from json import dumps as json_dumps
from django.db import models
from autoslug import AutoSlugField

from locations.models import Location



# Model: Director
class Director(models.Model):
    # Fields
    name = models.CharField(max_length=50)
    imdb_id = models.CharField(max_length=10, unique=True)

    # Representation
    def __unicode__(self):
        return self.name


# Model: Company
class Company(models.Model):
    # Fields
    name = models.CharField(max_length=80, unique=True)
    website = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=20, blank=True)

    # Metadata
    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    # Representation
    def __unicode__(self):
        return self.name


# Model: Production
class Production(models.Model):
    # Fields
    type = models.CharField(max_length=4, choices=(('film', 'Film'), ('show', 'Serie')))

    title = models.CharField(max_length=50)
    release = models.DateField('Released')
    summary = models.TextField(max_length=1000)
    directors = models.ManyToManyField(Director, blank=True)
    producers = models.ManyToManyField(Company, blank=True, related_name='producers')
    distributors = models.ManyToManyField(Company, blank=True, related_name='distributors')
    runtime = models.IntegerField(default=0)

    poster = models.ImageField(upload_to='posters/', blank=True)
    backdrop = models.ImageField(upload_to='backdrops/', blank=True)

    imdb_id = models.CharField(max_length=10, blank=True)
    tmdb_id = models.CharField(max_length=10, blank=True)
    nbdb_id = models.CharField(max_length=10, blank=True)
    tvdb_id = models.CharField(max_length=10, blank=True)

    slug = AutoSlugField(populate_from='title', editable=True, unique=True, always_update=True)


    @property
    def locations(self):
        locations = {}

        for scene in self.scene_set.all():
            if scene.location:
                if scene.location in locations:
                    locations[scene.location].append(scene)
                else:
                    locations[scene.location] = [scene]

        return locations


    @property
    def title_with_year(self):
        return '%s%s' % (self.title, ' (%s)' % (str(self.release.year) if self.release else ''))
    

    # Representation
    def __unicode__(self):
        return self.title



# Model: Scene
class Scene(models.Model):
    # Fields
    production = models.ForeignKey(Production)
    description = models.TextField(max_length=800, blank=True)
    location = models.ForeignKey('locations.Location', blank=True, null=True, on_delete=models.SET_NULL)


    # Representation
    def __unicode__(self):
        return '%s: %s' % (
            self.production.title,
            self.location.address if self.location else '(None)'
        )


# Model: Shot
class Shot(models.Model):
    # Fields
    scene = models.ForeignKey(Scene)
    image = models.ImageField(upload_to='shots/')
    timecode = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)


    # Representation
    def __unicode__(self):
        return '%s (%s,%s)' % (
            self.scene,
            str(self.latitude),
            str(self.longitude)
        )



'''

# QuerySet: Productions
class ProductionsQuerySet(models.QuerySet):
    def films(self):
        return self.filter(type='film')

    def series(self):
        return self.filter(type='show')

    def production(self, slug):
        return self.get(slug=slug)


# Model: Production
class Production(models.Model):
    # Fields
    type            = models.CharField(max_length=4, choices=(('film', 'Film'), ('show', 'Serie')))

    title           = models.CharField(max_length=50)
    release         = models.DateField('Released')
    summary         = models.TextField(max_length=800)
    directors       = models.ManyToManyField(Director, blank=True)
    producers       = models.ManyToManyField(Company, blank=True, related_name='producers')
    distributors    = models.ManyToManyField(Company, blank=True, related_name='distributors')
    runtime         = models.IntegerField(default=0)

    poster          = models.ImageField(upload_to='posters/', blank=True)
    backdrop        = models.ImageField(blank=True)

    imdb_id         = models.CharField(max_length=10, blank=True)
    tmdb_id         = models.CharField(max_length=10, blank=True)
    nbdb_id         = models.CharField(max_length=10, blank=True)
    tvdb_id         = models.CharField(max_length=10, blank=True)

    slug            = AutoSlugField(populate_from='title', editable=True, unique=True, always_update=True)

    # Scene count
    def scene_count(self):
        return self.scene_set.count()

    # Location count
    def location_count(self):
        location_count = 0

        for scene in self.scene_set.all():
            if scene.location:
                location_count += 1

        return location_count

    # Locations
    def locations(self):
        locations = {}

        for scene in self.scene_set.all():
            if scene.location:
                if scene.location in locations:
                    locations[scene.location].append(scene)
                else:
                    locations[scene.location] = [scene]

        return locations

    # Manager
    productions = ProductionsQuerySet.as_manager()

    # Representation
    def __unicode__(self):
        return self.title

'''