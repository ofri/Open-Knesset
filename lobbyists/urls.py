#encoding: UTF-8
from django.conf.urls import url, patterns

from views import *

lobbyistpatterns = patterns ('',
	url(r'^lobbyists/$', LobbyistsIndexView.as_view(), name='lobbyists'),
	url(r'^lobbyists/(?P<pk>\d+)$', LobbyistsIndexView.as_view(), name='lobbyists'),
    url(r'^lobbyist/(?P<pk>\d+)$', LobbyistDetailView.as_view(), name='lobbyist-detail'),
    url(r'^lobbyist/(?P<pk>\d+)/(?P<sk>\d+)$', LobbyistDetailView.as_view(), name='lobbyist-detail'),
    url(r'^lobbyist/corporation/(?P<pk>\d+)$',
        LobbyistCorporationDetailView.as_view(), name='lobbyist-corporation'),
    url(r'^lobbyist/corporation/(?P<pk>\d+)/(?P<sk>\d+)$',
        LobbyistCorporationDetailView.as_view(), name='lobbyist-corporation'),
    url(r'^lobbyist/represent/(?P<pk>\d+)$',
        LobbyistRepresentDetailView.as_view(), name='lobbyist-represent'),
)
