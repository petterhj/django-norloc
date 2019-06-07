# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals
from json import dumps as json_dumps
from django.db import models
from autoslug import AutoSlugField
from uuid_upload_path import upload_to_factory
from autoslug.settings import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, Adjust
from django.dispatch import receiver

from locations.models import Location


# Upload factories
MIGRATE = False
upload_to_posters = upload_to_factory('posters') if not MIGRATE else 'posters'
upload_to_backdrops = upload_to_factory('backdrops') if not MIGRATE else 'backdrops'
upload_to_shots = upload_to_factory('shots') if not MIGRATE else 'shots'
upload_to_people = upload_to_factory('people') if not MIGRATE else 'people'
upload_to_logos = upload_to_factory('logos') if not MIGRATE else 'logos'



# Model: Production
class Production(models.Model):
    # Fields
    type = models.CharField(max_length=4, choices=(('film', 'Film'), ('tv', 'Serie')))

    title = models.CharField(max_length=50)
    release = models.DateField('Released')
    summary = models.TextField(max_length=1000, blank=True)
    summary_credit = models.CharField(max_length=50, blank=True)
    runtime = models.IntegerField(default=0, blank=True)
    
    directors = models.ManyToManyField('Person', blank=True, related_name='directors')
    writers = models.ManyToManyField('Person', blank=True, related_name='writers')
    photographers = models.ManyToManyField('Person', blank=True, related_name='photographers')
    producers = models.ManyToManyField('Company', blank=True, related_name='producers')
    distributors = models.ManyToManyField('Company', blank=True, related_name='distributors')
    
    poster = models.ImageField(upload_to=upload_to_posters, blank=True)

    tmdb_id = models.CharField(max_length=10, blank=False, unique=True)
    imdb_id = models.CharField(max_length=10, blank=True)
    nbdb_id = models.CharField(max_length=10, blank=True)

    slug = AutoSlugField(populate_from='slugified_title', editable=True, unique=True)#, always_update=True)


    # Metadata
    class Meta:
        ordering = ['title']


    # Clean
    def clean(self):
        # Super
        super(Production, self).clean()
        
        # Runtime
        if not self.runtime or self.runtime < 0:
            self.runtime = 0


    # Save
    def save(self, *args, **kwargs):
        super(Production, self).save(*args, **kwargs)

        # Update people
        # print('!'*1000)
        # print(self.directors.all())


    # Properties
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

    @property
    def slugified_title(self):
        populate_from = self.title

        if Production.objects.filter(slug=slugify(populate_from)):
            # populate_from = '%s-%s' % (self.title, self.release.year)
            populate_from = '%s-%s' % (self.title, self.release.split('-')[0])

        return slugify(populate_from)

    
    # Representation
    def __unicode__(self):
        return '%s (%s)' % (self.title, self.release.year)



# Model: Scene
class Scene(models.Model):
    # Fields
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    description = models.TextField(max_length=800, blank=True)
    location = models.ForeignKey('locations.Location', 
        blank=True, null=True, on_delete=models.SET_NULL
    )
    uncertain = models.BooleanField(default=False)

    
    # Representation
    def __unicode__(self):
        return '%s: %s' % (
            self.production.title,
            self.location.address if self.location else '(None)'
        )



# Model: Shot
class Shot(models.Model):
    # Fields
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_to_shots)
    double = models.BooleanField(default=False)
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



# Model: Person
class Person(models.Model):
    # Fields
    name = models.CharField(max_length=50)
    headshot = ProcessedImageField(**{
        'upload_to': upload_to_people, 
        'blank': True,
        'processors': [ResizeToFill(400, 400), Adjust(color=0)],
        'format': 'JPEG'
    })
    bio = models.TextField(max_length=1000, blank=True)
    bio_credit = models.CharField(max_length=50, blank=True)
    known_for_department = models.CharField(max_length=10, blank=True, choices=(
        ('directing', 'Regi'), ('writing', 'Manus'), ('photo', 'Foto')
    ))

    tmdb_id = models.CharField(max_length=10, blank=False, unique=True)
    imdb_id = models.CharField(max_length=10, blank=True)

    slug = AutoSlugField(populate_from='name', editable=True, unique=True, always_update=True)


    # Metadata
    class Meta:
        ordering = ['name']


    # Properties
    @property
    def job_title(self):
        titles = []
        if self.directors.count() > 0:
            titles.append('Regi')
        if self.writers.count() > 0:
            titles.append('Manus')
        if self.photographers.count() > 0:
            titles.append('Foto')
        return '/'.join(titles)

    @property
    def productions(self):
        productions = self.writers.all() | self.directors.all() | self.photographers.all()
        return productions.distinct().order_by('-release')

    
    # Representation
    def __unicode__(self):
        return self.name



# Model: Company
class Company(models.Model):
    # Fields
    name = models.CharField(max_length=80, unique=True)
    logo = models.ImageField(upload_to=upload_to_logos, blank=True)
    website = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=20, blank=True)

    
    # Meta
    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']

    
    # Representation
    def __unicode__(self):
        return self.name



