from django.views.generic import ListView, DetailView
from models import LobbyistHistory, Lobbyist

class LobbyistsIndexView(ListView):

    queryset = LobbyistHistory.objects.latest().lobbyists.order_by('person__name')


class LobbyistDetailView(DetailView):

    model = Lobbyist

    def get_context_data(self, **kwargs):
        context = super(LobbyistDetailView, self).get_context_data(**kwargs)
        context['represents'] = context['object'].latest_data.represents.all()
        return context
