'''
the knesset's context processor is here. 

 for more on Django's context processors:
     http://www.b-list.org/weblog/2006/jun/14/django-tips-template-context-processors/
'''
import re
from django.utils.translation import ugettext as _
from django.conf import settings

DEFAULT_STATE = 'vote'
STATE_NAMES = {
    'member': _('Members'),
    'party': _('Parties'),
    'vote': _('Past Votes'),
}
url = re.compile(r'(?P<state>\w+)/(?:(?P<pk>\d+)/)?$')

def processor(request):
    d = dict()
    m = url.match(request.path)
    state = m and m.group('state') or DEFAULT_STATE
    try:
        d['PAGE_BASE_NAME'] = STATE_NAMES[state]
    except KeyError:
        d['PAGE_BASE_NAME'] = STATE_NAMES[DEFAULT_STATE]
    
    d['fb_api_key'] = settings.FACEBOOK_API_KEY

    return d
