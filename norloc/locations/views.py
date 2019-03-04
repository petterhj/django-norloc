# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals

import simplejson as json

from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count

from common.views import error, not_found
from .models import Location, NO_COUNTIES


# JSON: Locations
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
        'locations': locations
    })


def location(request, county, place, slug):
    location = get_object_or_404(Location, county=county, place_slug=place, slug=slug)

    # return JsonResponse({'name': location.full_address})
    return render(request, 'location.html', {
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