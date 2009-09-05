from django.conf.urls.defaults import *
from knesset.mks.views import list, detail

urlpatterns = patterns('',
    url(r'^$', list, name='list'),
    url(r'^(\d+)/$', 'knesset.mks.views.detail'),
)
