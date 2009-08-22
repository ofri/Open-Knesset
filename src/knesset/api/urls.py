from django.conf.urls.defaults import *
from piston.resource import Resource
from knesset.api.handlers import *

vote_handler = Resource(VoteHandler)
vote_details_handler = Resource(VoteDetailsHandler)
member_handler = Resource(MemberHandler)
party_handler = Resource(PartyHandler)

context = dict(emitter_format='json')

urlpatterns = patterns('',
      url(r'^vote/$', vote_handler, context),
      url(r'^vote/(?P<vote_id>[^/]+)/$', vote_details_handler, context),
      url(r'^member/((?P<member_id>[^/]+)/)?', member_handler, context),
      url(r'^party/((?P<party_id>[^/]+)/)?', party_handler, context),
      )

