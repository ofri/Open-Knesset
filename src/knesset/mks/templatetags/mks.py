from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def mk(m, icons=''):
    ''' renders a member - m - using its name and displaing the following
    icon comibnations:
        'w' - member is being watched
        'x' - removes a member
    '''

    r =  u'<a class="hashnav item dontwrap" id="detail-%(id)s"'
    r += u'href="%(url)s" title="%(name)s">'
    if 'w' in icons:
        r += '<img class="watched-member" id="watching-%(id)s" src="%(icon_path)s/eye.png">'
    elif 'x' in icons:
        r += '<img class="can-delete-member" id="can-delete-%(id)s" src="%(icon_path)s/X.png">'
    r += '&nbsp;%(name)s</a>'

    c = dict(id=m.id, url=m.get_absolute_url(), name=m.name,
             icon_path= '%s/img' % settings.MEDIA_URL)

    return r % c




