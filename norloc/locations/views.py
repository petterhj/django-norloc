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

from .models import Location


# JSON: Locations
def locations(request):
    # Locations
    locations = {l.pk: {
        'full_address': l.full_address,
        # 'bounds': [[p.latitude, p.longitude] for p in l.bounds.all()],
        'bounds': l.bounds if l.bounds else [],
    } for l in Location.objects.all()}

    # Return JSON
    return JsonResponse(locations)


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