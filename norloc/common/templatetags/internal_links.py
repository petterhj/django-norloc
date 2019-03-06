# -*- coding: utf-8 -*-

# Imports
import re
import logging
from django import template
from django.core.urlresolvers import reverse
from productions.views import *


# Logger
logger = logging.getLogger('norloc')


# Template library
register = template.Library()


# Filter: Internal links
@register.filter
def internal_links(value):
    """
    Takes a markdown textfield, and searches for internal links in the format:

    {{view:slug}}

    Inspired, and simplified, by https://djangosnippets.org/snippets/10420/ 
    """

    link_types_views = {
        'production': production,
    }

    try:
        pattern = re.compile(r'{{(\S+):(\S+):(\S+)}}')
        
        for (view, production_type, slug) in re.findall(pattern, value):
            if view not in link_types_views:
                raise Exception('invalid view name')

            resolved = reverse(link_types_views[view], args=(production_type, slug, ))

            value = value.replace('{{%s:%s:%s}}' % (view, production_type, slug), resolved)

    except:
        logger.exception('Could not parse internal link')
        return value
    
    return value