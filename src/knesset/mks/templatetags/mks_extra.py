from django import template

register = template.Library()

@register.filter
def party_link(o): 
    "return a link to party object o"
    return ''




