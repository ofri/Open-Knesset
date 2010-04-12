from django import template

register = template.Library()

@register.simple_tag
def mk(o): 
    ''' renders a member '''
    
    r =  u'<a class="hashnav item dontwrap" id="detail-%(id)s"'
    r += u'href="%(url)s" title="%(name)s">'
    r +=   u'%(name)s&nbsp;%(icons)s'
    r += u'</a>&nbsp;'

    c = dict(id=o.id, url=o.get_absolute_url(), name=o.name)
    try:
        c['icons']=o.extra
    except AttributeError:
        c['icons']=''

    return r % c




