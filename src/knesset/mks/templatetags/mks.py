from django import template
from django.conf import settings
from knesset.links.models import Link

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

class GetMemberFor(template.Node):
    ''' usage: {% get_member_for post as var %}
    This templatetag return the member associated with a specific object
    curently, only the Post object is supported 
    '''
    def __init__(self, object_var_name, return_var_name):
        self.object_var_name = object_var_name
        self.return_var_name = return_var_name
    def render(self, context):
        p = context[self.object_var_name]
        try:
            context[self.return_var_name] = Link.objects.filter(url=p.feed.url)[0].content_object
        except:
            context[self.return_var_name] = None
        return ''

import re
def do_get_member_for(parser, token):
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(\w+) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    object_var_name, return_var_name = m.groups()
    return GetMemberFor(object_var_name, return_var_name)
register.tag('get_member_for', do_get_member_for)

