#encoding: UTF-8
from django.conf.urls.defaults import *
from django.utils.translation import ugettext
from knesset.hashnav.views import ListDetailView
from knesset.hashnav import ListView
from models import *
from views import *

vote_view = VoteListView(queryset = Vote.objects.all(),paginate_by=20, extra_context={'votes':True,'title':ugettext('Votes')})
law_view = ListView(queryset=Law.objects.filter(title__contains='חוק').order_by('title'), paginate_by=20, extra_context={'title':ugettext('Laws')})
bill_view = BillView(queryset=Bill.objects.all().filter(law__merged_into=None).order_by('-stage_date'), paginate_by=20,extra_context={'title':ugettext('Bills')})

lawsurlpatterns = patterns ('',
    url(r'^bill/$', bill_view, name='bill-list'),
    url(r'^bill/knesset-booklet/(?P<booklet_num>\d+)/$', bill_by_knesset_booklet, name='bill-by-knesset-booklet'),
    url(r'^bill/(?P<object_id>\d+)/$', bill_view, name='bill-detail'),
    url(r'^law/$', law_view, name='law-list'),
    url(r'^law/(?P<object_id>\d+)/$', law_view, name='law-detail'),
    url(r'^vote/$', vote_view, name='vote-list'),
    url(r'^(?P<object_type>\w+)/(?P<object_id>\d+)/suggest-tag/$', suggest_tag),
    url(r'^(?P<object_type>\w+)/(?P<object_id>\d+)/tag-votes/(?P<tag_id>\d+)/(?P<vote>[+\-\d]+)/$', vote_on_tag),  
    url(r'^vote/(?P<object_id>\d+)/$', vote_view, name='vote-detail'),
    url(r'^votes/tagged/(?P<tag>.*)/$', tagged, name='tagged-votes'),    
)
