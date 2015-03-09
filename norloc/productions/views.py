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