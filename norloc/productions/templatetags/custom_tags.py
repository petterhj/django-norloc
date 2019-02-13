from json import dumps
from django import template

register = template.Library()

@register.filter
def as_tags(field, attrs):
    value_attr = attrs.split(',')[0]
    image_attr = attrs.split(',')[1]
    tags = []

    for o in field.all():
        image = getattr(o, image_attr)
        image_url = image.url if image else None

        tags.append({
            'pk': o.pk,
            'value': getattr(o, value_attr),
            'image': image_url
        })

    return dumps(tags)