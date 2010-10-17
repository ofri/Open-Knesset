#encoding: UTF-8
from django.conf.urls.defaults import *
from django.utils.translation import ugettext
from knesset.hashnav import ListView, DetailView
from models import *
from views import MeetingsListView, MeetingDetailView, CommitteeDetailView, meeting_list_by_date

committees_list = ListView(queryset = Committee.objects.all(),paginate_by=20)
committee_detail = CommitteeDetailView(queryset = Committee.objects.all())
meetings_list = MeetingsListView(queryset = CommitteeMeeting.objects.all(),paginate_by=20)
#meeting_list_by_date = MeetingListByDate(paginate_by=20)
meeting_details = MeetingDetailView(queryset = CommitteeMeeting.objects.all())

committeesurlpatterns = patterns ('',
    url(r'^committee/$', committees_list, name='committee-list'),
    url(r'^committee/(?P<object_id>\d+)/$', committee_detail, name='committee-detail'),
    url(r'^committee/(?P<committee_id>\d+)/all_meetings/$', meetings_list, name='committee-all-meetings'),
    url(r'^committee/(?P<committee_id>\d+)/date/(?P<date>[\d\-]+)/$', meeting_list_by_date, name='committee-meetings-by-date'),
    url(r'^committee/(?P<committee_id>\d+)/date/$', meeting_list_by_date, name='committee-meetings-by-date'),
    url(r'^committee/meeting/(?P<object_id>\d+)/$', meeting_details, name='committee-meeting'),

)
