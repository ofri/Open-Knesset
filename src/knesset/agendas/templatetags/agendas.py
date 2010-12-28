from django import template
from django.conf import settings
from knesset.links.models import Link
from knesset.agendas.models import Agenda, AgendaVote
from knesset.agendas.forms import VoteLinkingForm, VoteLinkingFormSet

register = template.Library()

@register.inclusion_tag('agendas/agendasfor.html')
def agendas_for(user, vote):
    ''' renders the relevent agenda for the vote and a form for the 
        agendas the given user can edit
    '''
    editable = []
    if user.is_authenticated():
        for a in user.agendas.all():
            r = {'agenda_name': a.name, 'agenda_id': a.id, 'vote_id': vote.id}
            try:
                av = a.agendavotes.get(vote=vote)
                r['weight'] = av.score
                r['reasoning'] = av.reasoning
            except AgendaVote.DoesNotExist:
                r['weight'] = 0.0
                r['reasoning'] = u''
            editable.append(r)
                  
    return { 'formset': editable and VoteLinkingFormSet(initial = editable),
             'agendavotes': AgendaVote.objects.filter(agenda__in=Agenda.objects.get_relevant_for_user(user)).distinct(),
           }
