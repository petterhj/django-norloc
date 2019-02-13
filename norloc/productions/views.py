# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals

import logging
import tmdbsimple as tmdb
from requests import get
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.conf import settings
from uuid_upload_path import upload_to_factory

from lib.tmdb import TMDb
from lib.image_from_url import ImageFileFromUrl

from .models import Production, Scene, Shot, Person


# Logger
logger = logging.getLogger('norloc')


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

    edit_request = bool(request.GET.get('edit', False))
    edit_mode = edit_request and request.user.is_authenticated()

    logger.info('Rendering production, slug=%s, edit_mode=%r (requested=%r, auth=%r)' % (
        production.slug, edit_mode, edit_request, request.user.is_authenticated()
    ))

    # Render template
    return render(request, 'production.html', {
        'edit_mode': edit_mode,
        'production': production
    })


# View: Person
def person(request, slug):
    # Person
    person = get_object_or_404(Person, slug=slug)

    # Render template
    return render(request, 'person.html', {
        'person': person
    })


# View: Import production
@login_required
def import_production(request, tmdb_id=None):
    # Search
    if not tmdb_id:
        # Render import search template
        logger.info('Rendering search template (no TMDb ID provided)')
        return render(request, 'import_production.html', {})

    # Check if production exists
    existing = Production.objects.filter(tmdb_id=tmdb_id).first()

    if existing:
        # Redirect to production
        logger.info('Production (tmdb_id=%s) already exists, redirecting' % (tmdb_id))
        return redirect(reverse('production', args=[existing.slug]) + '?edit=true')

    # Get details
    try:
        details = TMDb().details(tmdb_id)
        is_valid = 'NO' in details.get('production_countries', {}).keys()
    
    except:
        logger.exception('Could not get TMDb details')
        return error(request)

    else:
        # Check if allowed production country
        if not details or not is_valid or existing:
            logger.error('Importing production aborted, no details, not valid or exists')
            return error(request)

        # Create production instance
        try:
            logger.info('Creating new production object, title=%s' % (details.get('title')))

            p = Production(**{
                'type': 'film', 
                'title': details.get('title'),
                'release': details.get('release'),
                'summary': details.get('overview'),
                'runtime': details.get('runtime'),
                'imdb_id': details.get('imdb_id'),
                'tmdb_id': details.get('tmdb_id'),
            })

            p.save()

        except:
            logger.exception('Could not create production instance')
            return error(request)

        else:
            # Save poster
            try:
                logger.info('Adding poster, %s' % (details.get('poster')))
                p.poster.save('poster.jpg', ImageFileFromUrl(details.get('poster')), save=True)

            except:
                logger.exception('Could not save poster')

            # Add crew
            for job in ['directors', 'writers', 'photographers']:
                logger.info('Adding %d %s to production' % (len(details.get(job, [])), job))

                for person in details.get(job, []):
                    try:
                        # Get existing, or create, person object
                        pr, created = Person.objects.get_or_create(tmdb_id=person['tmdb_id'], defaults={
                            'name': person['name']
                        })

                        people = getattr(p, job)
                        people.add(pr)

                    except:
                        logger.exception('Could not add person')


            # Redirect to production view
            return redirect(production, slug=p.slug)

    # Error occured
    return error(request)

    
# View: Error
def error(request, message=None):
    # Render template  
    return render(request, 'error.html', {
        'message': message if message else ':(('
    })


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


# JSON: People tags
def people_tags(request):
    # Return JSON
    return JsonResponse({
        'people': [{
            'pk': p.pk,
            'value': p.name,
            'image': p.headshot.url if p.headshot else None
        } for p in Person.objects.all()]
    })


# JSON: TMDb search
@login_required
def tmdb_search(request):
    # Search
    title = request.GET.get('title', '').encode('utf-8')
    results = {'films': []}

    if not title:
        return JsonResponse(results)

    try:
        results['films'] = TMDb().search(title, limit=5)
    except:
        logger.exception('Could not search TMDb')
        return JsonResponse(results)

    # Response
    return JsonResponse(results)


# JSON: TMDb details
@login_required
def tmdb_details(request, tmdb_id):
    # Fetch movie details from TMDb
    try:
        details = TMDb().details(tmdb_id)
    except:
        logger.exception('Could not get TMDb details')
        return JsonResponse({})

    # Response
    return JsonResponse(details)