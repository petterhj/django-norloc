# -*- coding: utf-8 -*-

# Imports
from json import dumps, loads
from django import forms
from django.apps import apps
from django.core.urlresolvers import reverse_lazy
from django.contrib.staticfiles.templatetags.staticfiles import static

from .models import Production, Person



# ModelForm: StyledModelForm
class StyledModelForm(forms.ModelForm):
    def is_valid(self, *args, **kwargs):
        # Super
        valid = super(StyledModelForm, self).is_valid(*args, **kwargs)

        # Errors
        errors = self.errors.as_data()

        for field, validation_errors in errors.iteritems():
            # Update field attributes
            attr_class = self.fields[field].widget.attrs.get('class', '')
            # attr_title = '\n'.join([u'%s (%s)' % (e.message, e.code) for e in validation_errors])

            self.fields[field].widget.attrs.update({
                'class': attr_class + ' error'
            })
            print self.fields[field].widget.attrs, '!!'*20

        return valid



# Widget: ImageSelect
class ImageSelect(forms.ClearableFileInput):
    template_name = 'widgets/imageselect.html'

    class Media:
        css = {'all': ('css/widget.imageselect.css',)}
        js = ('js/widget.imageselect.js',)



# Widget: TagsInput
class TagsInput(forms.TextInput):
    '''
    Partly inspired by "django-searchable-select"
    '''

    # Init
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        self.source = kwargs.pop('source')
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
        return super(TagsInput, self).render(name, dumps(tags), attrs={
            'data-source': self.source
        })


    # Value from data
    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value:
            return [o['pk'] for o in loads(value)]
        return []


# ModelForm: Production
class ProductionForm(StyledModelForm):
    # Meta
    class Meta:
        model = Production

        fields = [
            'poster', 'title', 'release', 'summary', 'summary_credit', 'runtime',
            'directors', 'writers', 'photographers', 'producers', 'distributors',
            'imdb_id', 'tmdb_id', 'nbdb_id',
        ]

        widgets = {
            'poster': ImageSelect({'srccleared': static('img/no-poster.png')}),
            'title': forms.TextInput({'placeholder': 'Tittel'}),
            'release': forms.TextInput({'placeholder': 'Permiere'}),
            'summary': forms.Textarea({'placeholder': 'Sammendrag'}),
            'summary_credit': forms.TextInput({'placeholder': 'Kreditering (sammendrag)'}),
            'runtime': forms.NumberInput({'placeholder': 'Lengde'}),

            'directors': TagsInput(**{
                'model': 'productions.Person',
                'source': reverse_lazy('people_tags'),
                'fields': {'value': 'name', 'image': 'headshot'},
                'attrs': {'class': 'tagify', 'placeholder': 'Regi'}
            }),
            'writers': TagsInput(**{
                'model': 'productions.Person',
                'source': reverse_lazy('people_tags'),
                'fields': {'value': 'name', 'image': 'headshot'},
                'attrs': {'class': 'tagify', 'placeholder': 'Manus'}
            }),
            'photographers': TagsInput(**{
                'model': 'productions.Person',
                'source': reverse_lazy('people_tags'),
                'fields': {'value': 'name', 'image': 'headshot'},
                'attrs': {'class': 'tagify', 'placeholder': 'Foto'}
            }),

            'producers': TagsInput(**{
                'model': 'productions.Company',
                'source': reverse_lazy('companies_tags'),
                'fields': {'value': 'name', 'image': 'logo'},
                'attrs': {'class': 'tagify', 'placeholder': 'Produksjon'}
            }),
            'distributors': TagsInput(**{
                'model': 'productions.Company',
                'source': reverse_lazy('companies_tags'),
                'fields': {'value': 'name', 'image': 'logo'},
                'attrs': {'class': 'tagify', 'placeholder': 'Distribusjon'}
            }),

            'imdb_id': forms.TextInput({'placeholder': 'IMDb ID'}),
            'tmdb_id': forms.TextInput({'placeholder': 'TMDb ID'}),
            'nbdb_id': forms.TextInput({'placeholder': 'NBdb ID'}),
        }


# ModelForm: Person
class PersonForm(forms.ModelForm):
    # Meta
    class Meta:
        model = Person

        fields = [
            'headshot', 'name', 'bio', 'bio_credit',
            'imdb_id', 'tmdb_id',
        ]

        widgets = {
            'headshot': ImageSelect({'srccleared': static('img/no-headshot.png')}),
            'name': forms.TextInput({'placeholder': 'Navn'}),
            'bio': forms.Textarea({'placeholder': 'Biografi'}),
            'bio_credit': forms.TextInput({'placeholder': 'Kreditering (biografi)'}),
            'imdb_id': forms.TextInput({'placeholder': 'IMDb ID'}),
            'tmdb_id': forms.TextInput({'placeholder': 'TMDb ID'}),
        }