import json

from django import template
from django.conf import settings
from knesset.links.models import Link
from knesset.agendas.models import Agenda, AgendaVote, Party
from knesset.agendas.forms import VoteLinkingForm, VoteLinkingFormSet
from django.core.cache import cache

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
                r['weight'] = None
                r['reasoning'] = u''
            editable.append(r)
    
#    import pdb
#    pdb.set_trace()
    return { 'formset': editable and VoteLinkingFormSet(initial = editable),
             'agendavotes': AgendaVote.objects.filter(agenda__in=Agenda.objects.get_relevant_for_user(user),vote=vote).distinct(),
           }

@register.inclusion_tag('agendas/agenda_list_item.html')
def agenda_list_item(agenda, watched_agendas=None):

    cached_context = cache.get('agenda_parties_%d' % agenda.id)
    if not cached_context:
        selected_parties = agenda.selected_instances(Party, top=20,bottom=0)['top']
        cached_context = {'selected_parties': selected_parties }
        cache.set('agenda_parties_%d' % agenda.id, cached_context, 900)
    party_scores = [(val.name, val.score) for val in cached_context['selected_parties']]
    enumerated_party = [(idx+0.5, values[0]) for idx, values in enumerate(party_scores)]
    enumerated_score = [(idx, values[1]) for idx, values in enumerate(party_scores)]
    
    return {'agenda': agenda,
            'watched_agendas': watched_agendas,
            'party_scores': json.dumps(enumerated_score, ensure_ascii=False),
            'party_list': json.dumps(enumerated_party, ensure_ascii=False)}

