from django.conf.urls.defaults import patterns, url
from .views import PendingSuggestionsView, PendingSuggestionsCountView


urlpatterns = patterns('',
    url('^pending/$', PendingSuggestionsView.as_view(),
        name='suggestions_pending'),
    url('^pending_count/$', PendingSuggestionsCountView.as_view(),
        name='suggestions_pending_count'),
)
