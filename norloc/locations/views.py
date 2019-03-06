# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals

import logging
import simplejson as json

from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Count

from common.views import error, not_found
from .models import Location, NO_COUNTIES, LOCATION_TYPES
from .forms import LocationForm


# Logger
logger = logging.getLogger('norloc')


# View/JSON: Locations
def locations(request, county=None, place=None, json=False):
    # Filter
    locations = Location.objects
    
    if county:
        locations = locations.filter(county=county)

    if place:
        locations = locations.filter(place_slug=place)

    locations = locations.all().annotate(production_count=Count('scene__production', distinct=True))

    # elif filter in ['film', 'tv']:
    #     # Filter by type
    #     productions = Production.objects.filter(type={
    #         'film': 'film',
    #         'tv': 'show',
    #     }.get(filter)).order_by('-release')

    # else:
    #     # Invalid filter
    #     return not_found(request)


    # Locations in JSON format
    if json:
        # Return JSON
        return JsonResponse({l.pk: {
            'full_address': l.full_address,
            # 'bounds': [[p.latitude, p.longitude] for p in l.bounds.all()],
            'bounds': l.bounds if l.bounds else [],
        } for l in locations})

    # Render template
    return render(request, 'locations.html', {
        # 'filter': filter,
        'counties': NO_COUNTIES,
        'location_types': LOCATION_TYPES,
        'locations': locations
    })


# View: Location
def location(request, county, place, slug):
    # Location
    location = get_object_or_404(Location, county=county, place_slug=place, slug=slug)
    edit_request = bool(request.GET.get('edit', False))
    edit_mode = edit_request and request.user.is_authenticated()
    form = None

    # Edit location (GET)
    if request.method == 'GET' and edit_mode:
        # Form
        form = LocationForm(instance=location)

    # Update location (POST)
    if request.method == 'POST' and edit_mode:
        form = LocationForm(instance=location, data=request.POST)#, files=request.FILES)
        
        logger.info('Checking if form is valid')
        
        if form.is_valid():
            # Save
            logger.info('Form valid, saving posted data')
            form.save()

            # Redirect
            return redirect(reverse('location', args=[form.instance.county, form.instance.place_slug, form.instance.slug]) + '?edit=true')

        else:
            logger.error('Form invalid')
            logger.debug(dict(form.errors.items()))

    # Render template
    logger.info('Rendering location (%s), slug=%s, edit_mode=%r (requested=%r, auth=%r)' % (
        request.method, location.slug, edit_mode, edit_request, request.user.is_authenticated()
    ))

    return render(request, 'location.html', {
        'edit_mode': edit_mode,
        'form': form if edit_mode else None,
        'location': location
    })


# JSON: Location details
def location_details(request, lpk):
    # Location
    location = get_object_or_404(Location, pk=lpk)

    # Return JSON
    return JsonResponse({
        'pk': location.pk,
        'address': location.address,
        'municipality': location.municipality,
        'county': location.county,
        'description': location.description,
    })


# JSON: Update location bounds
@login_required
@require_POST
def update_location_bounds(request, lpk):
    # Location
    location = get_object_or_404(Location, pk=lpk)

    print '~'*50
    print location.bounds
    print location.bounds_locked
    print '~'*50

    if not request.is_ajax():
        return JsonResponse({'success': False})

    try:
        # Parse data
        bounds = json.loads(request.body)
            
        # Update location bounds
        location.bounds = bounds
        location.save()

    except:
        raise
        return JsonResponse({'success': False})

    # Return JSON
    return JsonResponse({'success': True})