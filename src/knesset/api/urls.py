from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.emitters import Emitter

from knesset.api.handlers import *

vote_handler = Resource(VoteHandler)
member_handler = Resource(MemberHandler)
party_handler = Resource(PartyHandler)
tag_handler = Resource(TagHandler)

urlpatterns = patterns('',
      url(r'^vote/$', vote_handler),
      url(r'^vote/(?P<id>[0-9]+)/$', vote_handler),
      url(r'^member/$', member_handler, name='member-handler'),
      url(r'^member/(?P<id>[0-9]+)/$', member_handler),
      url(r'^party/$', party_handler),
      url(r'^party/(?P<id>[0-9]+)/$', party_handler),
      url(r'^tag/$', tag_handler),
      url(r'^tag/(?P<id>[0-9]+)/$', tag_handler),
      url(r'^tag/vote/(?P<vote_id>[0-9]+)/$', tag_handler),
      )

