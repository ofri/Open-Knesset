# Create your views here.
from django.views.generic import ListView
from django.utils.translation import ugettext as _
from hashnav.detail import DetailView
from agendas.models import Agenda
from polyorg.models import CandidateList

class CandidateListListView(ListView):
    model = CandidateList

class CandidateListDetailView(DetailView):
    model = CandidateList

    def get_context_data (self, **kwargs):
        context = super(CandidateListDetailView, self).get_context_data(**kwargs)
        cl = context['object']
        agendas = []
        if cl.member_ids:
            for a in Agenda.objects.filter(is_public=True):
                agendas.append({'id': a.id, 
                                'name': a.name,
                                'url': a.get_absolute_url(),
                                'score': a.candidate_list_score(cl)})
            context['agendas'] = agendas
            context['stats'] = cl.voting_statistics
        return context
        
        '''
        candidate_list = context['object']
        context['maps_api_key'] = settings.GOOGLE_MAPS_API_KEY

        if self.request.user.is_authenticated():
            agendas = Agenda.objects.get_selected_for_instance(party, user=self.request.user, top=3, bottom=3)
        else:
            agendas = Agenda.objects.get_selected_for_instance(party, user=None, top=3, bottom=3)
        agendas = agendas['top'] + agendas['bottom']
        for agenda in agendas:
            agenda.watched=False
        if self.request.user.is_authenticated():
            watched_agendas = self.request.user.get_profile().agendas
            for watched_agenda in watched_agendas:
                if watched_agenda in agendas:
                    agendas[agendas.index(watched_agenda)].watched = True
                else:
                    watched_agenda.score = watched_agenda.party_score(party)
                    watched_agenda.watched = True
                    agendas.append(watched_agenda)
        agendas.sort(key=attrgetter('score'), reverse=True)

        context.update({'agendas':agendas})
        '''
        return context

