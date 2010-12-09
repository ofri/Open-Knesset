from django.conf import settings
from django.conf.urls.defaults import *
from knesset.mks.models import Member, Party
from knesset.hashnav import DetailView
from views import *
from feeds import MemberActivityFeed

member_list_view = MemberListView(queryset = Member.objects.all(),extra_context = {'past_mks':Member.objects.filter(is_current=False)}) 
member_detail_view = MemberDetailView(queryset = Member.objects.all())
party_list_view = PartyListView(queryset = Party.objects.all()) 
party_detail_view = PartyDetailView(queryset = Party.objects.all(),extra_context = {'maps_api_key':settings.GOOGLE_MAPS_API_KEY})

mksurlpatterns = patterns('knesset.mks.views',
    url(r'^member/$', member_list_view, name='member-list'),
    url(r'^member/(?P<object_id>\d+)/$', member_detail_view, name='member-detail'),
    url(r'^member/(?P<object_id>\d+)/rss/$', MemberActivityFeed(), name='member-activity-feed'),
    url(r'^member/(?P<object_id>\d+)/(?P<slug>[\w\-\"]+)/$', member_detail_view, name='member-detail-with-slug'),
    # TODO:the next url is hardcoded in a js file
    url(r'^member/auto_complete/$', member_auto_complete, name='member-auto-complete'),
    url(r'^member/search/?$', member_by_name, name='member-by-name'), 
    url(r'^party/$', party_list_view, name='party-list'),
    url(r'^party/(?P<object_id>\d+)/$', party_detail_view, name='party-detail'),
    url(r'^party/(?P<object_id>\d+)/(?P<slug>[\w\-\"]+)/$', party_detail_view, name='party-detail-with-slug'),
    url(r'^party/search/?$', party_by_name, name='party-by-name'),
)
