# -*- coding: utf-8 -*-

# Imports
from json import dumps, loads
from django import forms
from django.apps import apps

from .models import Production, Person


# Widget: TagsInput
class TagsInput(forms.TextInput):
    '''
    Partly inspired by "django-searchable-select"
    '''

    # Init
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        self.fields = kwargs.pop('fields')
        super(TagsInput, self).__init__(*args, **kwargs)


    # Render
    def render(self, name, value, attrs=None):
        # Model
        model = apps.get_model(self.model)

        # Tags
        tags = []
        objects = model.objects.filter(pk__in=value)

        for o in objects:
            tag_value = getattr(o, self.fields.get('value'))
            tag_image = getattr(o, self.fields.get('image'))
            tag_image = tag_image.url if tag_image else None

            tags.append({
                'pk': o.pk,
                'value': tag_value,
                'image': tag_image,
            })

        # Value
        return super(TagsInput, self).render(name, dumps(tags), attrs=None)


    # Value from data
    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value:
            return [o['pk'] for o in loads(value)]
        return []



# ModelForm: Production
class ProductionForm(forms.ModelForm):
    # Meta
    class Meta:
        model = Production

        fields = [
            'title', 'release', 'summary', 'summary_credit',
            'directors', 'writers', 'photographers',
            'imdb_id', 'tmdb_id', 'nbdb_id', 'tvdb_id'
        ]

        widgets = {
            'title': forms.TextInput({'placeholder': 'Tittel'}),
            'release': forms.TextInput({'placeholder': 'Permiere'}),
            'summary': forms.Textarea({'placeholder': 'Sammendrag'}),
            'summary_credit': forms.TextInput({'placeholder': 'Kreditering (sammendrag)'}),

            'directors': TagsInput(**{
                'model': 'productions.Person',
                'fields': {'value': 'name', 'image': 'headshot'},
                'attrs': {'class': 'tagify', 'placeholder': 'Regi'}
            }),
            'writers': TagsInput(**{
                'model': 'productions.Person',
                'fields': {'value': 'name', 'image': 'headshot'},
                'attrs': {'class': 'tagify', 'placeholder': 'Manus'}
            }),
            'photographers': TagsInput(**{
                'model': 'productions.Person',
                'fields': {'value': 'name', 'image': 'headshot'},
                'attrs': {'class': 'tagify', 'placeholder': 'Foto'}
            }),

            'imdb_id': forms.TextInput({'placeholder': 'IMDb ID'}),
            'tmdb_id': forms.TextInput({'placeholder': 'TMDb ID'}),
            'nbdb_id': forms.TextInput({'placeholder': 'NBdb ID'}),
            'tvdb_id': forms.TextInput({'placeholder': 'TVDb ID'}),
        }

    # Save
    def save(self):
        print '~'*50
        print self.cleaned_data
        print '~'*50

        # Initial
        production = super(ProductionForm, self).save(commit=True)
        '''

        # Save
        production.save()

        return production
        '''