# Imports
import json

from django.core import serializers
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from locations.models import Location


# View: Index
def index(request):
    # Locations
    locations = Location.objects.all()

    # Render
    if request.GET.get('api') == 'json':
        # JSON
        data = []

        for location in locations:
            data.append({
                'address': location.address,
                'bounds':  [{
                    'latitude': p.latitude,
                    'longitude': p.longitude
                } for p in location.bounds.all()],
                'scenes': [{
                    'production': {
                        'slug': s.production.slug,
                        'title': s.production.title,
                        'year': s.production.release.year,
                    },
                    'shots': [{
                        'latitude': sh.point.latitude if sh.point else None,
                        'longitude': sh.point.longitude if sh.point else None
                    } for sh in s.shot_set.all()]
                } for s in location.scene_set.all()]
            });

        return HttpResponse(json.dumps(data), content_type='application/json')

    else:
        # Paginator
        paginator = Paginator(locations, 24)

        page = request.GET.get('page')

        try:
            locs = paginator.page(page)
        except PageNotAnInteger:
            # Return first page
            locs = paginator.page(1)
        except EmptyPage:
            # Page out of range: return last page
            locs = paginator.page(paginator.num_pages)

        # Template
        return render_to_response(
            'locations.html',
            {'locations': locs},
            context_instance=RequestContext(request)
        )


# View: Map
def map(request):
    # Template
    return render_to_response(
        'map.html',
        {

        },
        context_instance=RequestContext(request)
    )
