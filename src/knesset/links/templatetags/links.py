from django import template
from knesset.links.models import Link
from django.conf import settings

register = template.Library()

@register.inclusion_tag('links/_object_links.html')
def object_links(object):
    l = Link.objects.for_model(object)
    return {'links': l, 'MEDIA_URL': settings.MEDIA_URL}

