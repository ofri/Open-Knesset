from django.conf.urls.defaults import *
from knesset.mks.models import Member, Party
from knesset.hashnav.views import ListDetailView
                       
member_view = ListDetailView(queryset = Member.objects.all(),) # filter(end_date__gte=yearstart(2009)),
party_view = ListDetailView(queryset = Party.objects.all(),) 
mksurlpatterns = patterns('knesset.mks.views',
    url(r'^member/$', member_view, name='member-list'),
    url(r'^member/(?P<object_id>\d+)/$', member_view, name='member-detail'),
    url(r'^member/(?P<object_id>\d+)/(?P<slug>[\w\-\"]+)/$', member_view, name='member-detail-with-slug'),
    url(r'^party/$', party_view, name='party-list'),
    url(r'^party/(?P<object_id>\d+)/$', party_view, name='party-detail'),
    url(r'^party/(?P<object_id>\d+)/(?P<slug>[\w\-\"]+)/$', party_view, name='party-detail-with-slug'),

)
