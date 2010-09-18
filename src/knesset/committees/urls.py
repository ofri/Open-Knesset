#encoding: UTF-8
from django.conf.urls.defaults import *
from django.utils.translation import ugettext
from knesset.hashnav import ListView, DetailView
from models import *
from views import MeetingsListView, MeetingDetailView, meeting_list_by_date

committees_list = ListView(queryset = Committee.objects.all(),paginate_by=20)
meetings_list = MeetingsListView(queryset = CommitteeMeeting.objects.all(),paginate_by=20)
#meeting_list_by_date = MeetingListByDate(paginate_by=20)
meeting_details = MeetingDetailView(queryset = CommitteeMeeting.objects.all())

committeesurlpatterns = patterns ('',
    url(r'^committee/$', committees_list, name='committee-list'),
    url(r'^committee/(?P<committee_id>\d+)/$', meetings_list, name='committee-detail'),
    url(r'^committee/(?P<committee_id>\d+)/date/(?P<date>[\d\-]+)/$', meeting_list_by_date, name='committee-meetings-by-date'),
    url(r'^committee/meeting/(?P<object_id>\d+)/$', meeting_details, name='committee-meeting'),

)
