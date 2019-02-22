# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Count

from lib.tmdb import TMDb
from lib.image_from_url import ImageFileFromUrl

from .models import Production, Scene, Shot, Person, Company
from .forms import ProductionForm, PersonForm


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
    form = None

    # Edit production (GET)
    if request.method == 'GET' and edit_mode:
        # Form
        form = ProductionForm(instance=production)

    # Update production (POST)
    if request.method == 'POST' and edit_mode:
        # print '='*50
        # print request.POST#.get("title", "")
        # print request.FILES
        # Form
        form = ProductionForm(instance=production, data=request.POST, files=request.FILES)
        
        logger.info('Checking if form is valid')
        
        if form.is_valid():
            # Save
            logger.info('Form valid, saving posted data')
            form.save()

            # Redirect
            return redirect(reverse('production', args=[form.instance.slug]) + '?edit=true')

        else:
            logger.error('Form invalid')
            logger.debug(dict(form.errors.items()))

    # Render template
    logger.info('Rendering production (%s), slug=%s, edit_mode=%r (requested=%r, auth=%r)' % (
        request.method, production.slug, edit_mode, edit_request, request.user.is_authenticated()
    ))

    return render(request, 'production.html', {
        'edit_mode': edit_mode,
        'form': form if edit_mode else None,
        'production': production
    })


# View: People
def people(request, filter=None):
    # Filter
    if not filter:
        people = Person.objects.annotate(
            production_count=Count('directors', distinct=True) + Count('writers', distinct=True) + Count('photographers', distinct=True)
        ).order_by('-production_count')

    elif filter in ['regi', 'manus', 'foto']:
        # Filter by role
        people = Person.objects.annotate(
            production_count=Count({
                'regi': 'directors',
                'manus': 'writers',
                'foto': 'photographers',
            }.get(filter), distinct=True)
        ).filter(production_count__gt=0).order_by('-production_count')

    else:
        # Invalid filter
        return error(request)

    # Render template
    return render(request, 'people.html', {
        # 'people': Person.objects.all()#order_by('-release')
        'filter': filter,
        'people': people

    })


# View: Person
def person(request, slug):
    # Person
    person = get_object_or_404(Person, slug=slug)
    edit_request = bool(request.GET.get('edit', False))
    edit_mode = edit_request and request.user.is_authenticated()
    form = None

    # Edit person (GET)
    if request.method == 'GET' and edit_mode:
        # Form
        form = PersonForm(instance=person)

    # Update person (POST)
    if request.method == 'POST' and request.user.is_authenticated():
        # Form
        form = PersonForm(instance=person, data=request.POST, files=request.FILES)
        
        logger.info('Checking if form is valid')
        
        if form.is_valid():
            # Save
            logger.info('Form valid, saving posted data')
            form.save()

            # Redirect
            return redirect(reverse('person', args=[form.instance.slug]) + '?edit=true')

        else:
            logger.error('Form invalid')
            logger.debug(dict(form.errors.items()))

    # Render template
    logger.info('Rendering person (%s), slug=%s, edit_mode=%r (requested=%r, auth=%r)' % (
        request.method, person.slug, edit_mode, edit_request, request.user.is_authenticated()
    ))

    # Render template
    return render(request, 'person.html', {
        'edit_mode': edit_mode,
        'form': form if edit_mode else None,
        'person': person
    })


# View: Import person
@login_required
def import_person(request, tmdb_id=None):
    # Search
    if not tmdb_id:
        # Render import search template
        logger.info('Rendering search template (no TMDb ID provided)')
        return render(request, 'import_person.html', {})


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
        'tags': [{
            'pk': p.pk,
            'value': p.name,
            'image': p.headshot.url if p.headshot else None
        } for p in Person.objects.all()]
    })


# JSON: Companies tags
def companies_tags(request):
    # Return JSON
    return JsonResponse({
        'tags': [{
            'pk': p.pk,
            'value': p.name,
            'image': p.logo.url if p.logo else None
        } for p in Company.objects.all()]
    })


# JSON: TMDb production search
@login_required
def tmdb_production_search(request):
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


# JSON: TMDb production details
@login_required
def tmdb_production_details(request, tmdb_id):
    # Fetch movie details from TMDb
    try:
        details = TMDb().details(tmdb_id)
    except:
        logger.exception('Could not get TMDb details')
        return JsonResponse({})

    # Response
    return JsonResponse(details)


# JSON: TMDb people search
@login_required
def tmdb_people_search(request):
    # Search
    name = request.GET.get('name', '').encode('utf-8')
    results = {'persons': []}

    if not name:
        return JsonResponse(results)

    try:
        results['persons'] = TMDb().people_search(name, limit=5)
    except:
        logger.exception('Could not search TMDb')
        return JsonResponse(results)

    # Response
    return JsonResponse(results)


# JSON: TMDb person details
@login_required
def tmdb_person_details(request, tmdb_id):
    # Fetch movie details from TMDb
    try:
        details = TMDb().person_details(tmdb_id)
    except:
        logger.exception('Could not get TMDb details')
        return JsonResponse({})

    # Response
    return JsonResponse(details)