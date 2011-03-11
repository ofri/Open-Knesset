from django.conf import settings
from django.conf.urls.defaults import *
from views import *
from feeds import MemberActivityFeed

mksurlpatterns = patterns('knesset.mks.views',
    url(r'^member/$', MemberListView.as_view(), name='member-list'),
    url(r'^member/(?P<pk>\d+)/$', 'mk_detail', name='member-detail'),
    url(r'^member/(?P<object_id>\d+)/rss/$', MemberActivityFeed(), name='member-activity-feed'),
    url(r'^member/(?P<pk>\d+)/(?P<slug>[\w\-\"]+)/$', 'mk_detail', name='member-detail-with-slug'),
    # TODO:the next url is hardcoded in a js file
    url(r'^member/auto_complete/$', member_auto_complete, name='member-auto-complete'),
    url(r'^member/search/?$', member_by_name, name='member-by-name'), 
    url(r'^party/$', PartyListView.as_view(), name='party-list'),
    url(r'^party/(?P<pk>\d+)/$', PartyDetailView.as_view(), name='party-detail'),
    url(r'^party/(?P<pk>\d+)/(?P<slug>[\w\-\"]+)/$', PartyDetailView.as_view(), name='party-detail-with-slug'),
    url(r'^party/search/?$', party_by_name, name='party-by-name'),
)
