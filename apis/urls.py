from django.conf.urls import url, patterns, include
from piston.resource import Resource
from django.views.decorators.cache import cache_page

from handlers import VoteHandler
from handlers import BillHandler
from handlers import MemberHandler
from handlers import PartyHandler
from handlers import TagHandler
from handlers import AgendaHandler
from handlers import CommitteeHandler
from handlers import CommitteeMeetingHandler
from handlers import EventHandler

from resources import v2_api

vote_handler = cache_page(60*15)(Resource(VoteHandler))
bill_handler = cache_page(60*15)(Resource(BillHandler))
member_handler = cache_page(60*15)(Resource(MemberHandler))
party_handler = cache_page(60*15)(Resource(PartyHandler))
tag_handler = cache_page(60*15)(Resource(TagHandler))
agenda_handler = cache_page(60*15)(Resource(AgendaHandler))
committee_handler = cache_page(60*15)(Resource(CommitteeHandler))
committee_meeting_handler = cache_page(60*15)(Resource(CommitteeMeetingHandler))
event_handler = cache_page(60*15)(Resource(EventHandler))

urlpatterns = patterns('',
      url(r'^vote/$', vote_handler, name='vote-handler'),
      url(r'^vote/(?P<id>[0-9]+)/$', vote_handler, name='vote-handler'),
      url(r'^bill/$', bill_handler, name='bill-handler'),
      url(r'^bill/(?P<id>[0-9]+)/$', bill_handler, name='bill-handler'),
      url(r'^bill/popular/$', bill_handler, name='popular-bills-handler', kwargs={'popular': True}),
      url(r'^member/$', member_handler, name='member-handler'),
      url(r'^member/(?P<id>[0-9]+)/$', member_handler, name='member-handler'),
      url(r'^party/$', party_handler, name='party-handler'),
      url(r'^party/(?P<id>[0-9]+)/$', party_handler, name='party-handler'),
      url(r'^tag/$', tag_handler, name='tag-handler'),
      url(r'^tag/(?P<id>[0-9]+)/$', tag_handler, name='tag-handler'),
      url(r'^tag/(?P<app_label>\w+)/(?P<object_type>\w+)/(?P<object_id>[0-9]+)/$', tag_handler, name='tag-handler'),
      url(r'^agenda/$', agenda_handler, name='agenda-handler'),
      url(r'^agenda/(?P<id>[0-9]+)/$', agenda_handler, name='agenda-handler'),
      url(r'^agenda/(?P<app_label>\w+)/(?P<object_type>\w+)/(?P<object_id>[0-9]+)/$', agenda_handler, name='agenda-handler'),
      url(r'^committee/$', committee_handler, name='committe-handler'),
      url(r'^committee/(?P<id>[0-9]+)/$', committee_handler, name='committe-handler'),
      url(r'^committeemeeting/$', committee_meeting_handler, name='committee-meeting-handler'),
      url(r'^committeemeeting/(?P<id>[0-9]+)/$', committee_meeting_handler, name='committee-meeting-handler'),
      url(r'^event/$', event_handler, name='event-handler'),
      url(r'^event/(?P<id>[0-9]+)/$', event_handler, name='event-handler'),
      # NOTE: this view is not in the api application, but in the events application
      url(r'^event/icalendar/$', 'events.views.icalendar', name='event-icalendar'),
      url(r'^event/icalendar/(?P<summary_length>\d+)/$', 'events.views.icalendar', name='event-icalendar'),
      (r'^', include(v2_api.urls)),
      url(r'^v2/doc/', include('tastypie_swagger.urls', namespace='v2api_tastypie_swagger'),
          kwargs={"tastypie_api_module":"apis.resources.v2_api", "namespace":"v2api_tastypie_swagger", "version": "2.0"})
      )
