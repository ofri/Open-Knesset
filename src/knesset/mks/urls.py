from django.conf.urls.defaults import *
from knesset.mks.views import *

mksurlpatterns = patterns('knesset.mks.views',
    url(r'^member/$', 'member', name='member-list'),
    url(r'^member/(\d+)/$', 'member', name='member-detail'),
    url(r'^party/$', 'party', name='party-list'),
    url(r'^party/(\d+)/$', 'party', name='party-detail'),

)
