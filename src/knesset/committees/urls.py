#encoding: UTF-8
from django.conf.urls.defaults import *
from django.utils.translation import ugettext
from knesset.hashnav.views import ListDetailView
from models import *
from views import *

committees_view = CommitteesView(queryset = Committee.objects.all(),paginate_by=20)
committee_meeting_view = CommitteeMeetingView(queryset = CommitteeMeeting.objects.all(),paginate_by=20)

committeesurlpatterns = patterns ('',
    url(r'^committee/$', committees_view, name='committee-list'),
    url(r'^committee/(?P<object_id>\d+)/$', committees_view, name='committee-detail'),
    url(r'^committee/(?P<committee_id>\d+)/all_meetings/$', committee_meeting_view, name='committee-all-meetings'),
    url(r'^committee/meeting/(?P<object_id>\d+)/$', committee_meeting_view, name='committee-meeting'),

)
