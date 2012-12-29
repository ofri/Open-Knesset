from django.conf.urls.defaults import *
from views import BadgeTypeDetailView, BadgeTypeListView

detail_view = BadgeTypeDetailView.as_view()
list_view = BadgeTypeListView()

urlpatterns = patterns('',
    url(r'^$', list_view, name='all-badge-list'),
    url(r'^(?P<pk>\d+)/$', detail_view, name='badge-detail'),
)
