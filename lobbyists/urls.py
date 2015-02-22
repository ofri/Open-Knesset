#encoding: UTF-8
from django.conf.urls import url, patterns

from views import *

lobbyistpatterns = patterns ('',

    # Lobbyist corporations
    # Currently the main page of lobbyists shows the corporations (sorry for the confusion)
    url(r'^lobbyists/$', LobbyistCorporationsListView.as_view(), name='lobbyists'),
    url(r'^lobbyist/corporation/(?P<pk>\d+)$',
        LobbyistCorporationDetailView.as_view(), name='lobbyist-corporation'),

    # Lobbyists
	url(r'^lobbyist/(?P<pk>\d+)$', LobbyistDetailView.as_view(), name='lobbyist-detail'),

    # Lobbyist Represents
    url(r'^lobbyist/represent/(?P<pk>\d+)$',
        LobbyistRepresentDetailView.as_view(), name='lobbyist-represent'),

    # Edit actions
    url(r'^lobbyist/corporation/mark_alias/(?P<alias>\d+)/(?P<main>\d+)$',
        LobbyistCorporationMarkAliasView),

    # auto complete
    url(r'^lobbyist/auto_complete/$',
        lobbyists_auto_complete,
        name='lobbyists-auto-complete'),
)
