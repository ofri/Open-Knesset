#encoding: UTF-8
from django.conf.urls.defaults import *
from django.views.generic import DetailView

from models import *

urlpatterns = patterns ('',
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(
        model=Topic, context_object_name = 'topic'), name='topic-detail'),
)

