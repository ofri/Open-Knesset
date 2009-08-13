from django.conf.urls.defaults import *
from piston.resource import Resource
from knesset.api.handlers import VoteHandler

vote_handler = Resource(VoteHandler)

urlpatterns = patterns('',
      url(r'^vote/(?P<vote_id>[^/]+)/',
          vote_handler,
          { 'emitter_format': 'json' }),
      )

