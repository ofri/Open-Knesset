from django import template
from knesset.links.models import Link

register = template.Library()

@register.inclusion_tag('links/_links_as_table.html')
def object_links_as_table(object):
    l = Link.objects.for_model(object)
    return {'links': l}

@register.inclusion_tag('links/_links_as_div.html')
def object_links_as_div(object):
    l = Link.objects.for_model(object)
    return {'links': l}


