from django.conf.urls.defaults import *
from knesset.badges.views import *

detail_view = BadgeTypeDetailView.as_view()
list_view = BadgeTypeListView()

urlpatterns = patterns('',
    url(r'^$',list_view,name='all-badge-list'),
    url(r'^(?P<object_id>\d+)/$',detail_view,name='badge-detail'),
)
