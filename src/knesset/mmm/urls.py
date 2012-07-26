from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import ListView
from mmm.models import Document


mmmurlpatterns = patterns('',
    url(r'^mmm-documents/member/(?P<mid>\d+)/$', 
        'knesset.mmm.views.member_docs',
        name='member_mmms'),
    url(r'^mmm-documents/committee/(?P<cid>\d+)/$', 
        'knesset.mmm.views.committee_docs', 
        name='committe_mmms'),
)