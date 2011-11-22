from django.conf.urls.defaults import *
from piston.resource import Resource
from django.views.decorators.cache import cache_page

from knesset.api.handlers import *

vote_handler = cache_page(Resource(VoteHandler), 60*15)
bill_handler = cache_page(Resource(BillHandler), 60*15)
member_handler = cache_page(Resource(MemberHandler), 60*15)
party_handler = cache_page(Resource(PartyHandler), 60*15)
tag_handler = cache_page(Resource(TagHandler), 60*15)
agenda_handler = cache_page(Resource(AgendaHandler), 60*15)
committee_handler = cache_page(Resource(CommitteeHandler), 60*15)
committee_meeting_handler = cache_page(Resource(CommitteeMeetingHandler), 60*15)

urlpatterns = patterns('',
      url(r'^vote/$', vote_handler, name='vote-handler'),
      url(r'^vote/(?P<id>[0-9]+)/$', vote_handler, name='vote-handler'),
      url(r'^bill/$', bill_handler, name='bill-handler'),
      url(r'^bill/(?P<id>[0-9]+)/$', bill_handler, name='bill-handler'),
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
      # NOTE: this view is not in the api application, but in the events application
      url(r'^event/icalendar/$', 'knesset.events.views.icalendar'),
      )

