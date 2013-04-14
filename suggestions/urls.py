from django.conf.urls.defaults import patterns, url
from .views import (PendingSuggestionsView, PendingSuggestionsCountView,
                    AutoApplySuggestionView)


urlpatterns = patterns('',
    url('^pending/$', PendingSuggestionsView.as_view(),
        name='suggestions_pending'),
    url('^pending_count/$', PendingSuggestionsCountView.as_view(),
        name='suggestions_pending_count'),
    url('^auto_apply/(?P<pk>\d+)/$', AutoApplySuggestionView.as_view(),
        name='suggestions_auto_apply'),
)
