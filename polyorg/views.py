# Create your views here.
from django.views.generic import ListView
from django.utils.translation import ugettext as _
from hashnav.detail import DetailView
from polyorg.models import CandidateList, Candidate

class CandidateListListView(ListView):
    model = CandidateList

class CandidateListDetailView(DetailView):
    model = CandidateList

    '''
    TODO: get the agenda ranking for list to work
    '''
    def get_context_data (self, **kwargs):
        context = super(CandidateListDetailView, self).get_context_data(**kwargs)
        candidate_list = context['object']

        context['head'] = candidate_list.getHeadName()
        context['candidates'] = Candidate.objects.filter(candidates_list=candidate_list).order_by('ordinal')
#        context['maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
#
#        if self.request.user.is_authenticated():
#            agendas = Agenda.objects.get_selected_for_instance(party, user=self.request.user, top=3, bottom=3)
#        else:
#            agendas = Agenda.objects.get_selected_for_instance(party, user=None, top=3, bottom=3)
#        agendas = agendas['top'] + agendas['bottom']
#        for agenda in agendas:
#            agenda.watched=False
#        if self.request.user.is_authenticated():
#            watched_agendas = self.request.user.get_profile().agendas
#            for watched_agenda in watched_agendas:
#                if watched_agenda in agendas:
#                    agendas[agendas.index(watched_agenda)].watched = True
#                else:
#                    watched_agenda.score = watched_agenda.party_score(party)
#                    watched_agenda.watched = True
#                    agendas.append(watched_agenda)
#        agendas.sort(key=attrgetter('score'), reverse=True)
#
#        context.update({'agendas':agendas})
        return context


