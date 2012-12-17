from django import template
register = template.Library()

@register.inclusion_tag('user/_user.html')
def user(u):
    return {'user': u}
