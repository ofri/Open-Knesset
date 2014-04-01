from django.views.generic import ListView, DetailView
from models import LobbyistHistory, Lobbyist

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
