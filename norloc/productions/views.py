# Imports
import json

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response

from productions.models import Production


# View: Index
def index(request, type=None):
    # Productions
    productions = Production.productions
    
    if type:
        productions = productions.films() if type == 'films' else productions.series()

    productions = productions.order_by('-release')

    # Render
    return render_to_response(
        'productions.html',
        {'productions': productions},
        context_instance=RequestContext(request)
    )


# View: Production
def production(request, slug):
    # Production
    production = Production.productions.production(slug)

     # Render
    if request.GET.get('api') == 'json':
        # JSON
        data = {
            'title': production.title,
            'year': production.release.year,
            'poster': production.poster.url,
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
            {'production': production},
            context_instance=RequestContext(request)
        )