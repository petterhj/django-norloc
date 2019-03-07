# -*- coding: utf-8 -*-

# Imports
from django.db import models
from urlparse import urlparse


# Model: Reference
class Reference(models.Model):
    # Fields
    production = models.ForeignKey('productions.Production', null=True, blank=True)
    location = models.ForeignKey('locations.Location', null=True, blank=True)

    title = models.CharField(max_length=100)
    quote = models.TextField(max_length=350, blank=True)
    date = models.DateField('Published')
    source = models.URLField(max_length=200)


    # Properties
    @property
    def display_url(self):
    	return urlparse(self.source).hostname