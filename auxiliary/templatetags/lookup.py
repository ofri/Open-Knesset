from django import template

register = template.Library()


@register.filter(name='lookup')
def lookup(lookup_in, index):
    if index in lookup_in:
        return lookup_in[index]
    return ''
