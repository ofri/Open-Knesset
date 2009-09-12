from django.conf.urls.defaults import *
from views import vote
from models import Vote

lawsurlpatterns = patterns ('',
    url(r'^vote/$', vote, name='vote-list'),
    url(r'^vote/(\d+)/$', vote, name='vote-detail'),
)
