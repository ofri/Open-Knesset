from django.conf.urls.defaults import *
from knesset.mks.models import Member, Party
from knesset.hashnav.views import ListDetailView
from views import *
                       
member_view = MemberListView(queryset = Member.objects.all(),extra_context = {'past_mks':Member.objects.filter(is_current=False)}) 
party_view = PartyListView(queryset = Party.objects.all(),) 
member_select = MemberSelectView(queryset = Member.objects.all(),extra_context = {'past_mks':Member.objects.filter(is_current=False)})

mksurlpatterns = patterns('knesset.mks.views',
    url(r'^member/$', member_view, name='member-list'),
    url(r'^member/select/$', member_select, {'template_name':'mks/member_select.html'}, name='member-select'),
    url(r'^member/(?P<object_id>\d+)/$', member_view, name='member-detail'),
    url(r'^member/(?P<object_id>\d+)/(?P<slug>[\w\-\"]+)/$', member_view, name='member-detail-with-slug'),
    url(r'^party/$', party_view, name='party-list'),
    url(r'^party/(?P<object_id>\d+)/$', party_view, name='party-detail'),
    url(r'^party/(?P<object_id>\d+)/(?P<slug>[\w\-\"]+)/$', party_view, name='party-detail-with-slug'),

)
