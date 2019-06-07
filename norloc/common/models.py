# -*- coding: utf-8 -*-

# Imports
from django.db import models
from urllib.parse import urlparse


# Model: Reference
class Reference(models.Model):
    # Fields
    production = models.ForeignKey('productions.Production', 
        null=True, blank=True, on_delete=models.CASCADE
    )
    location = models.ForeignKey('locations.Location', 
        null=True, blank=True, on_delete=models.CASCADE
    )

    title = models.CharField(max_length=100)
    quote = models.TextField(max_length=350, blank=True)
    date = models.DateField('Published')
    source = models.URLField(max_length=200)


    # Metadata
    class Meta:
        ordering = ['-date']


    # Properties
    @property
    def display_url(self):
        return urlparse(self.source).hostname