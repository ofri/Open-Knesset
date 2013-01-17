from django import template
from django.conf import settings
from links.models import Link

register = template.Library()


@register.inclusion_tag('links/_object_links.html')
def object_links(object):
    l = Link.objects.for_model(object)
    return {'links': l, 'MEDIA_URL': settings.MEDIA_URL}


@register.inclusion_tag('links/_object_icon_links.html')
def object_icon_links(obj):
    "Display links as icons, to match the new design"
    l = Link.objects.for_model(obj)
    return {'links': l}
