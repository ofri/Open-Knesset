from django import template
from django.conf import settings
from knesset.links.models import Link
from knesset.agendas.models import Agenda, AgendaVote
from knesset.agendas.forms import VoteLinkingForm, VoteLinkingFormSet

register = template.Library()

@register.inclusion_tag('agendas/editor_agendas.html')
def agendas_for(user, vote):
    ''' renders current user's agendas:

    output:

      html form for the user to update his agendas
    '''
    agendas = []
    for a in Agenda.objects.get_relevant_for_user(user):
        r = {'agenda_name': a.name, 'agenda_id': a.id, 'vote_id': vote.id }
        try:
            av = a.related_votes.get(vote=vote)
            r['weight'] = av.score
            r['reasoning'] = av.reasoning
        except AgendaVote.DoesNotExist:
            r['weight'] = 0.0
            r['reasoning'] = u''
        agendas.append(r)
                  
    return { 'agendas': VoteLinkingFormSet(initial = agendas) }
