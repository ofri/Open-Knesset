from django.views.generic import ListView, DetailView
from models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache


class LobbyistsIndexView(ListView):

    def get_queryset(self):
        return LobbyistHistory.objects.latest().lobbyists.select_related('person').order_by('person__name')
        
    def get_context_data(self, **kwargs):
        context = super(LobbyistsIndexView, self).get_context_data(**kwargs)
        corporations = LobbyistCorporation.objects.current_corporations().order_by('name')
        corporation_ids = corporations.values_list('id', flat=True)
        corporation_alias = LobbyistCorporationAlias.objects.filter(main_corporation__id__in=corporation_ids)
        corporation_alias = corporation_alias.values_list('main_corporation__id', 'alias_corporation__id')
        #main = dict(corporation_alias)
        alias = dict(map(reversed, corporation_alias))
        main = {}
        aliases = []
        for corporation in corporations:
            if alias.has_key(corporation.id):
                main_id = alias[corporation.id]
                if not main.has_key(main_id):
                    main[main_id] = []
                main[main_id].append(corporation.id)
                aliases.append(corporation.id)
        for corporation in corporations:
            if not main.has_key(corporation.id) and corporation.id not in aliases:
                main[corporation.id] = []
        context['alias'] = main
        corporations = LobbyistCorporation.objects.filter(id__in=main.keys()).order_by('name')
        context['corporations'] = corporations
        lobbyists_cached_data = []
        for lobbyist in context['object_list']:
            lobbyists_cached_data.append(lobbyist.cached_data)
        context['object_list'] = lobbyists_cached_data
        return context


class LobbyistDetailView(DetailView):

    model = Lobbyist

    def get_context_data(self, **kwargs):
        context = super(LobbyistDetailView, self).get_context_data(**kwargs)
        lobbyist = context['object']
        context['represents'] = lobbyist.latest_data.represents.all()
        context['corporation'] = lobbyist.latest_corporation
        context['data'] = lobbyist.latest_data
        return context


class LobbyistCorporationDetailView(DetailView):

    model = LobbyistCorporation

    def get_context_data(self, **kwargs):
        context = super(LobbyistCorporationDetailView, self).get_context_data(**kwargs)
        context['lobbyists'] = context['object'].latest_data.lobbyists.order_by('person__name')
        if context['object'] not in LobbyistCorporation.objects.current_corporations():
            context['warning_old_corporation'] = True
        return context


class LobbyistRepresentDetailView(DetailView):

    model = LobbyistRepresent

    def get_context_data(self, **kwargs):
        context = super(LobbyistRepresentDetailView, self).get_context_data(**kwargs)