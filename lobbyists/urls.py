#encoding: UTF-8
from django.conf.urls import url, patterns

from views import LobbyistsIndexView, LobbyistDetailView, LobbyistCorporationDetailView

lobbyistpatterns = patterns ('',
	url(r'^lobbyists/$', LobbyistsIndexView.as_view(), name='lobbyists'),
	url(r'^lobbyists/(?P<pk>\d+)$', LobbyistsIndexView.as_view(), name='lobbyists'),
    url(r'^lobbyist/(?P<pk>\d+)$', LobbyistDetailView.as_view(), name='lobbyist-detail'),
    url(r'^lobbyist/corporation/(?P<hp>.+)$', LobbyistCorporationDetailView.as_view(), name='lobbyist-corporation')
)
