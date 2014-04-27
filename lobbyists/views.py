from django.views.generic import ListView, DetailView
from models import LobbyistHistory, Lobbyist, LobbyistCorporation, LobbyistCorporationData, LobbyistData
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

class LobbyistsIndexView(ListView):

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is None:
            return LobbyistHistory.objects.latest().lobbyists.select_related('person').order_by('person__name')
        else:
            return LobbyistHistory.objects.get(id=pk).lobbyists.order_by('person__name')
        
    def get_context_data(self, **kwargs):
        context = super(LobbyistsIndexView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk', None)
        if pk is None:
            context['is_historical'] = False
            context['history'] = []
            prev_lobbyist_history = None
            for lobbyist_history in LobbyistHistory.objects.filter(scrape_time__isnull=False).order_by('-scrape_time'):
                if prev_lobbyist_history is not None:
                    context['history'].append((prev_lobbyist_history, lobbyist_history))
                prev_lobbyist_history = lobbyist_history
            context['history'].append((prev_lobbyist_history, None))
            context['corporations'] = LobbyistCorporation.objects.current_corporations().order_by('name')
        else:
            context['is_historical'] = True
            context['lobbyist_history'] = LobbyistHistory.objects.get(id=pk)
            try:
                context['corporations'] = context['lobbyist_history'].corporations.order_by('name')
            except ObjectDoesNotExist:
                pass
        lobbyists_cached_data = []
        for lobbyist in context['object_list']:
            lobbyists_cached_data.append(lobbyist.cached_data)
        context['object_list'] = lobbyists_cached_data
        return context


class LobbyistDetailView(DetailView):

    model = Lobbyist

    def get_context_data(self, **kwargs):
        context = super(LobbyistDetailView, self).get_context_data(**kwargs)
        data_id = self.kwargs.get('sk', None)
        if data_id is None:
            context['is_historical'] = False
            context['represents'] = context['object'].latest_data.represents.all()
            context['history'] = context['object'].data.order_by('-scrape_time')
            context['corporation'] = context['object'].latest_corporation
            context['data'] = context['object'].latest_data
        else:
            context['is_historical'] = True
            data = LobbyistData.objects.get(id=data_id)
            context['lobbyist'] = context['object']
            context['object'] = data
            context['data'] = data
            context['represents'] = data.represents.all()
            context['corporation'] = LobbyistCorporation.objects.get(source_id=data.corporation_id, name=data.corporation_name)
        return context


class LobbyistCorporationDetailView(DetailView):

    model = LobbyistCorporation

    def get_context_data(self, **kwargs):
        context = super(LobbyistCorporationDetailView, self).get_context_data(**kwargs)
        data_id = self.kwargs.get('sk', None)
        if data_id is None:
            context['is_historical'] = False
            context['lobbyists'] = context['object'].latest_data.lobbyists.order_by('person__name')
            context['history'] = context['object'].data.order_by('-scrape_time')
            if context['object'] not in LobbyistCorporation.objects.current_corporations():
                context['warning_old_corporation'] = True
        else:
            data = LobbyistCorporationData.objects.get(id=data_id)
            context['is_historical'] = True
            context['corporation'] = context['object']
            context['object'] = data
            context['lobbyists'] = data.lobbyists.order_by('person__name')
        return context