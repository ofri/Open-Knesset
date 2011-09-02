#encoding: UTF-8
from django.conf.urls.defaults import *
from django.views.generic import DetailView

from views import *
from models import *

urlpatterns = patterns ('',
    # TODO: delete this app - merge into committees
    # url(r'^$', TopicListView.as_view(), name = 'topic-list'),
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(
        model=Topic, context_object_name = 'topic'), name='topic-detail'),
)

