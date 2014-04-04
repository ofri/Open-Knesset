from django.views.generic import ListView, DetailView
from models import LobbyistHistory, Lobbyist, LobbyistCorporation, LobbyistCorporationData, LobbyistData

class LobbyistsIndexView(ListView):

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is None:
            return LobbyistHistory.objects.latest().lobbyists.order_by('person__name')
        else:
            return LobbyistHistory.objects.get(id=pk).lobbyists.order_by('person__name')
        
    def get_context_data(self, **kwargs):
        context = super(LobbyistsIndexView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk', None)
        if pk is None:
            context['is_historical'] = False
            context['history'] = LobbyistHistory.objects.filter(scrape_time__isnull=False).order_by('-scrape_time')
            context['corporations'] = LobbyistCorporation.objects.current_corporations().order_by('name')
        else:
            context['is_historical'] = True
            context['lobbyist_history'] = LobbyistHistory.objects.get(id=pk)
            context['corporations'] = context['lobbyist_history'].corporations.order_by('name')
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