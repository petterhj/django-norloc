# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals

# from tmdbv3api import TMDb, Movie
from tmdb3 import set_cache, set_key, set_locale, searchMovie

from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import Production, Scene, Shot



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
                    'uncertain': scene.uncertain,
                    'scene_count': scene.shot_set.count(),
                    'photos': [{
                        'photo': p.photo.url,
                        'credit': p.credit,
                        'license': p.license,
                    } for p in scene.location.photo_set.all()],
                    'scenes': []
                }
            
            locations[scene.location.pk]['scenes'].append({
                'description': scene.description,
                'shot_count': scene.shot_set.count(),
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


# JSON: TMDb Search
@login_required
def tmdb_search(request):
    # Results
    results = {'films': []}

    # Setup TMDb
    set_cache('null')
    set_key('8cca874e1c98f99621d8200be1b16bd0')
    set_locale('no', 'no')
    
    # Search
    title = request.GET.get('title', '').encode('utf-8')

    if title:
        for movie in searchMovie(title):
            results['films'].append({
                'title': movie.title,
                'originaltitle': movie.originaltitle,
                # 'poster': movie.poster,
                'summary': movie.overview,
                'runtime': movie.runtime,
                'countries': {c.code.lower(): c.name for c in movie.countries},
                'popularity': movie.popularity,
                'release': movie.releases.get('NO').releasedate if movie.releases.get('NO') else None,
                'directors': [p.name for p in movie.crew if p.job == 'Director'],
                'poster': movie.poster.geturl() if movie.poster else None,
                'imdb_id': movie.imdb,
                'tmdb_id': movie.id,
            })

        # Sort results
        results['films'] = sorted(results['films'], key=lambda f: f['popularity'], reverse=True) 

    # Return JSON
    return JsonResponse(results)



'''
# Imports
import json

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404

from productions.models import Production, Scene


# View: Index
def index(request, filter_type='all'):
    # Productions
    productions = Production.productions
    productions = productions.films() if filter_type == 'films' else productions.series() if filter_type == 'series' else productions
    productions = productions.order_by('-release')

    # Paginator
    paginator = Paginator(productions, 24)

    page = request.GET.get('page')

    try:
        prods = paginator.page(page)
    except PageNotAnInteger:
        # Return first page
        prods = paginator.page(1)
    except EmptyPage:
        # Page out of range: return last page
        prods = paginator.page(paginator.num_pages)

    # Render
    return render_to_response(
        'productions.html',
        {
            'productions': prods,
            'filter': {
                'type': filter_type
            }
        },
        context_instance=RequestContext(request)
    )


# View: Production
def production(request, slug):
    # Production
    production = get_object_or_404(Production, slug=slug)

     # Render
    if request.GET.get('api') == 'json':
        # JSON
        data = {
            'title': production.title,
            'year': production.release.year,
            'poster': production.poster.url if production.poster else '',
            'locations': {}
        }

        for scene in production.scene_set.all():
            data['locations'][scene.location.pk] = {'address': scene.location.address, 'scenes': {}}

        for scene in production.scene_set.all():
            data['locations'][scene.location.pk]['scenes'][scene.pk] = [{
                'url': s.image.url,
                'latitude': s.point.latitude,
                'longitude': s.point.longitude
            } for s in scene.shot_set.all()]

        return HttpResponse(json.dumps(data), content_type='application/json')

    else:
        return render_to_response(
            'production.html',
            {
                'production': production
            },
            context_instance=RequestContext(request)
        )


# View: Scene locator
def locator(request, slug, scene_id):
    # Scene
    scene = get_object_or_404(Scene, pk=scene_id)

    # Render
    return render_to_response(
        'locator.html',
        {
            'scene': scene,
            'production': scene.production
        },
        context_instance=RequestContext(request)
    )
'''