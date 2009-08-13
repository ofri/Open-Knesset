from django.conf.urls.defaults import *
from piston.resource import Resource
from knesset.api.handlers import VoteHandler, MemberHandler

vote_handler = Resource(VoteHandler)
member_handler = Resource(MemberHandler)

urlpatterns = patterns('',
      url(r'^vote/(?P<vote_id>[^/]+)/',
          vote_handler,
          { 'emitter_format': 'json' }),
      url(r'^member/(?P<member_id>[^/]+)/',
          member_handler,
          { 'emitter_format': 'json' }),
      )

