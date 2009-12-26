from django.conf.urls.defaults import *
from knesset.hashnav.views import ListDetailView
from models import Vote
from views import *

vote_view = ListDetailView(queryset = Vote.objects.all(),paginate_by=20) # filter(end_date__gte=yearstart(2009)),
lawsurlpatterns = patterns ('',
    url(r'^vote/$', vote_view, name='vote-list'),
    url(r'^vote/(?P<object_id>\d+)/submit-tags/$', submit_tags),
    url(r'^vote/(?P<object_id>\d+)/tag-votes/(?P<tag_id>\d+)/(?P<vote>[+\-\d]+)/$', vote_on_tag),  
    url(r'^vote/(?P<object_id>\d+)/$', vote_view, name='vote-detail'),
)
