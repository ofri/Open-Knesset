'''
the knesset's context processor is here. 

 for more on Django's context processors:
     http://www.b-list.org/weblog/2006/jun/14/django-tips-template-context-processors/
'''
from django.utils.translation import ugettext as _

STATES = {
    'member': _('Members'),
    'party': _('Parties'),
    'vote': _('Votes'),
}

def processor(request):
    # TODO: parse request.path and get the 'state' part
    return {'PAGE_BASE_NAME': STATES['member']}
