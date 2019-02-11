# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals

# from tmdbv3api import TMDb, Movie
# from tmdb3 import set_cache, set_key, set_locale, searchMovie
import tmdbsimple as tmdb

from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Production, Scene, Shot, Person



# View: Index
def index(request):
    # Render template
    template = loader.get_template('index.html')
    context = {'productions': Production.objects.order_by('-release')}
    
    return HttpResponse(template.render(context, request))


# View: Map
def map(request):
    # Render template
    template = loader.get_template('map.html')
    context = {}
    
    return HttpResponse(template.render(context, request))


# View: Production
def production(request, slug):
    # Production
    production = get_object_or_404(Production, slug=slug)

    # Render template
    template = loader.get_template('production.html')
    context = {'production': production}
    
    return HttpResponse(template.render(context, request))


# View: Person
def person(request, slug):
    # Person
    person = get_object_or_404(Person, slug=slug)

    # Render template
    template = loader.get_template('person.html')
    context = {'person': person}
    
    return HttpResponse(template.render(context, request))


# View: Import production
@login_required
def import_production(request):
    # Render template
    template = loader.get_template('import_production.html')
    context = {}
    
    return HttpResponse(template.render(context, request))


# JSON: Locations
def locations(request, ppk):
    # Production
    production = get_object_or_404(Production, pk=ppk)

    # Find all locations for given production
    locations = {}

    for scene in production.scene_set.all():
        if scene.location:
            if scene.location.pk not in locations:
                locations[scene.location.pk] = {
                    'full_address': scene.location.full_address,
                    'description': scene.location.description,
                    'description_credit': scene.location.description_credit,
                    # 'bounds': scene.location.bounds,
                    'uncertain': False,
                    'scene_count': scene.shot_set.count(),
                    'photos': [{
                        'photo': p.photo.url,
                        'credit': p.credit,
                        'license': p.license,
                    } for p in scene.location.photo_set.all()],
                    'scenes': []
                }

            locations[scene.location.pk]['uncertain'] = scene.uncertain
        
            locations[scene.location.pk]['scenes'].append({
                'description': scene.description,
                'shot_count': scene.shot_set.count(),
                'uncertain': scene.uncertain,
                'shots': [{
                    'image': s.image.url,
                    'timecode': s.timecode,
                    'double': s.double,
                    # 'point': {'lat': s.latitude, 'lng': s.longitude}
                } for s in scene.shot_set.order_by('timecode', 'pk')]
            })
            
    # Return JSON
    return JsonResponse(locations)


# JSON: Shots
def shots(request):
    # Return all shots with valid coordinate
    shots = {}

    for shot in Shot.objects.all():
        if shot.longitude and shot.latitude:
            shots[shot.pk] = {
                'coordinate': {'lat': shot.latitude, 'lng': shot.longitude},
                'image': shot.image.url if shot.image else None,
                'production': shot.scene.production.title,
            }
            
    # Return JSON
    return JsonResponse(shots)


# JSON: Scenes
def scenes(request):
    # Return all shots grouped by scene
    try:
        scenes = {scene.pk: {
            'production': scene.production.title_with_year,
            'shots': {shot.pk: {
                'image': shot.image.url if shot.image else None,
                'coordinate': {
                    'lat': shot.latitude,
                    'lng': shot.longitude,
                } if shot.latitude and shot.longitude else None,
            } for shot in scene.shot_set.all()}
        } for scene in Scene.objects.all()}
    
    except:
        raise
        scenes = {}

    # Return JSON
    return JsonResponse(scenes)


# JSON: TMDb search
@login_required
def tmdb_search(request):
    # TMDb
    tmdb.API_KEY = settings.TMDB_API_KEY
    search = tmdb.Search()

    # Search
    title = request.GET.get('title', '').encode('utf-8')
    results = {'films': []}

    if not title:
        return JsonResponse(results)

    # Results
    for movie in search.movie(query=title, language='no').get('results')[0:5]:
        print movie
        print '---'*10

        title = movie.get('original_title') or movie.get('title')
        poster_path = movie.get('poster_path')
        poster = 'https://image.tmdb.org/t/p/w200' + poster_path if poster_path else None

        results['films'].append({
            'id': movie.get('id'),
            'title': movie.get('title'),
            'original_language': movie.get('original_language'),
            'popularity': movie.get('popularity', 0),
            'overview': movie.get('overview'),
            'poster': poster,
            'release': movie.get('release_date')
        })

        # Sort results by popularity
        # results['films'] = sorted(results['films'], key=lambda f: f['popularity'], reverse=True) 

    # Response
    return JsonResponse(results)


# JSON: TMDb details
@login_required
def tmdb_details(request, tmdb_id):
    # TMDb
    tmdb.API_KEY = settings.TMDB_API_KEY

    print tmdb_id

    # Response
    return JsonResponse({})