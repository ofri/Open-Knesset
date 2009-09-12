from django.conf.urls.defaults import *
from knesset.mks.views import *

urlpatterns = patterns('',
    url(r'member/$', 'knesset.mks.views.member_list'),
    url(r'member/(\d+)/$', 'knesset.mks.views.member_detail'),
    url(r'party/$', 'knesset.mks.views.party_list'),
    url(r'party/(\d+)/$', 'knesset.mks.views.party_detail'),

)
