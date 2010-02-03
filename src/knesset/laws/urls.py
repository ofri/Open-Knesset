#encoding: UTF-8
from django.conf.urls.defaults import *
from django.utils.translation import ugettext
from knesset.hashnav.views import ListDetailView
from models import Vote
from views import *

vote_view = ListDetailView(queryset = Vote.objects.all(),paginate_by=20, extra_context={'votes':True,'title':ugettext('Votes')}) # filter(end_date__gte=yearstart(2009)),
law_approve_view = ListDetailView(queryset = Vote.objects.all().filter(title__contains='אישור החוק'),paginate_by=20, extra_context={'law_approve':True, 'title':ugettext('Law Approvals')})

lawsurlpatterns = patterns ('',
    url(r'^law-approve/$', law_approve_view, name='law-approve'),
    url(r'^vote/$', vote_view, name='vote-list'),
    url(r'^vote/(?P<object_id>\d+)/submit-tags/$', submit_tags),
    url(r'^vote/(?P<object_id>\d+)/tag-votes/(?P<tag_id>\d+)/(?P<vote>[+\-\d]+)/$', vote_on_tag),  
    url(r'^vote/(?P<object_id>\d+)/$', vote_view, name='vote-detail'),
    url(r'^votes/tagged/(?P<tag>.*)/$', tagged, name='tagged-votes'),    
)
