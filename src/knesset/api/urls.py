from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.emitters import Emitter

from knesset.emitters import DivEmitter
from knesset.api.handlers import *

Emitter.register('htmldiv', DivEmitter, 'text/html; charset=utf-8')

vote_handler = Resource(VoteHandler)
vote_details_handler = Resource(VoteDetailsHandler)
member_handler = Resource(MemberHandler)
party_handler = Resource(PartyHandler)

context = dict(emitter_format='json')

urlpatterns = patterns('',
      url(r'^vote/(?P<emitter_format>\w+)/$', vote_handler),
      url(r'^vote/(?P<vote_id>[^/]+)/(?P<emitter_format>\w+)/$', vote_details_handler),
      url(r'^member/(?:(?P<member_id>[^/]+)/)?(?P<emitter_format>.+)/$', member_handler),
      url(r'^party/(?:(?P<party_id>[^/]+)/)?(?P<emitter_format>.+)/$', party_handler),
      )

