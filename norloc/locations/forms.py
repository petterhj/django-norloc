# -*- coding: utf-8 -*-

# Imports
from django import forms

from django.contrib.staticfiles.templatetags.staticfiles import static

from .models import Location



# ModelForm: Location
class LocationForm(forms.ModelForm):
    # Meta
    class Meta:
        model = Location

        fields = [
            'address', 'place', 'county', 
            'description', 'description_credit',
            'location_type',
        ]

        # widgets = {
        #     'name': forms.TextInput({'placeholder': 'Navn'}),
        #     'bio': forms.Textarea({'placeholder': 'Biografi'}),
        #     'bio_credit': forms.TextInput({'placeholder': 'Kreditering (biografi)'}),
        #     'imdb_id': forms.TextInput({'placeholder': 'IMDb ID'}),
        #     'tmdb_id': forms.TextInput({'placeholder': 'TMDb ID'}),
        # }