from django.views.generic import ListView, DetailView, TemplateView
from models import LobbyistHistory, Lobbyist, LobbyistData

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
        else:
            context['is_historical'] = True
            context['lobbyist_history'] = LobbyistHistory.objects.get(id=pk)
        return context


class LobbyistDetailView(DetailView):

    model = Lobbyist

    def get_context_data(self, **kwargs):
        context = super(LobbyistDetailView, self).get_context_data(**kwargs)
        context['represents'] = context['object'].latest_data.represents.all()
        return context


class LobbyistCorporationDetailView(TemplateView):

    template_name = "lobbyists/lobbyist_corporation_detail.html"

    def get_context_data(self, **kwargs):
        corporation_id = self.kwargs.get('hp', None)
        lobbyist = LobbyistData.objects.latest_lobbyist_corporation(corporation_id = corporation_id)
        return {
            'corporation_name': lobbyist.corporation_name,
            'corporation_id': corporation_id,
            'lobbyists': LobbyistData.objects.get_corporation_lobbyists(corporation_id=corporation_id)
        }