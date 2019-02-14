# -*- coding: utf-8 -*-

# Imports
from json import dumps
from django import forms
from django.apps import apps
from django.forms.widgets import CheckboxSelectMultiple

from .models import Production, Person


class TagsField(forms.MultipleChoiceField):
    pass
    # def __init__(self, *args, **kwargs):
    #     super(TagsField, self).__init__(*args, **kwargs)


class TagsInput(forms.TextInput):
    # Init
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        self.fields = kwargs.pop('fields')
        super(TagsInput, self).__init__(*args, **kwargs)


    # Render
    def render(self, name, value, attrs=None):
        print '~'*50
        print name, type(value), attrs
        # values = get_model(self.model).objects.filter(pk__in=value)
        # print self.queryset.objects.filter(pk__in=value)
        # print self.queryset.directors.all()

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



# ModelForm: Production
class ProductionForm(forms.ModelForm):
    # Fields
    # directors = TagsField(queryset=Person.objects.all())

    # Meta
    class Meta:
        model = Production

        fields = [
            'title', 'release', 'summary', 'summary_credit',
            'directors',
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
                'attrs': {'class': 'tagify'}
            }),
            # 'directors': CheckboxSelectMultiple(),
            # 'directors': TagsInput({'placeholder': 'Regissører'}),

            'imdb_id': forms.TextInput({'placeholder': 'IMDb ID'}),
            'tmdb_id': forms.TextInput({'placeholder': 'TMDb ID'}),
            'nbdb_id': forms.TextInput({'placeholder': 'NBdb ID'}),
            'tvdb_id': forms.TextInput({'placeholder': 'TVDb ID'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProductionForm, self).__init__(*args, **kwargs)

        # self.fields["directors"].widget = CheckboxSelectMultiple()
        # self.fields["directors"].queryset = Person.objects.all()



    # Save
    def save(self):
        production = super(ProductionForm, self).save(commit=False)
        # user.username = user.email

        # Save
        # production.save()

        return production