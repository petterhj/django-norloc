# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals

import tmdbsimple as tmdb

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Production, Scene, Shot, Person



# View: Index
def index(request):
    # Render template  
    return render(request, 'index.html', {
        'productions': Production.objects.order_by('-release')
    })


# View: Map
def map(request):
    # Render template
    return render(request, 'map.html', {})


# View: Production
def production(request, slug):
    # Production
    production = get_object_or_404(Production, slug=slug)

    # Render template
    return render(request, 'production.html', {
        'production': production
    })


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
def import_production(request, tmdb_id=None):
    if tmdb_id:
        # Render template
        return render(request, 'error.html', {})        

    # Render template
    return render(request, 'import_production.html', {})


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
            'tmdb_id': movie.get('id'),
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

    # Movie details
    try:
        movie = tmdb.Movies(tmdb_id)
        details = movie.info(language='NO', append_to_response='credits')
    except:
        return JsonResponse({})

    import json
    print json.dumps(details, indent=4)

    title = details.get('original_title') or details.get('title')
    poster_base = 'https://image.tmdb.org/t/p/w500'
    crew = details.get('credits', {}).get('crew', [])

    details = {
        'tmdb_id': details.get('id'),
        'imdb_id': details.get('imdb_id'),
        'title': details.get('title'),
        'overview': details.get('overview'),
        'poster': poster_base + details.get('poster_path') if details.get('poster_path') else None,
        'release': details.get('release_date'),
        'languages': {l['iso_639_1']: l['name'] for l in details.get('spoken_languages', {})},
        'production_countries': {c['iso_3166_1']: c['name'] for c in details.get('production_countries', {})},
        'production_companies': [{
            'name': company.get('name'),
            'country': company.get('origin_country')
        } for company in details.get('production_companies')],
        'runtime': details.get('runtime'),
        'directors': [{
            'tmdb_id': person.get('id'),
            'name': person.get('name'),
            'image': poster_base + person.get('profile_path') if person.get('profile_path') else None,
        } for person in crew if person.get('job') == 'Director'],
        'writers': [{
            'tmdb_id': person.get('id'),
            'name': person.get('name'),
            'image': poster_base + person.get('profile_path') if person.get('profile_path') else None,
        } for person in crew if person.get('job') == 'Screenplay'],
        'photographers': [{
            'tmdb_id': person.get('id'),
            'name': person.get('name'),
            'image': poster_base + person.get('profile_path') if person.get('profile_path') else None,
        } for person in crew if person.get('job') == 'Director of Photography'],
    }

    # Response
    return JsonResponse(details)