import json

from django import template
from django.conf import settings
from knesset.links.models import Link
from knesset.agendas.models import (Agenda, AgendaVote, AgendaMeeting,
                                    AgendaBill, Party,
                                    UserSuggestedVote)
from knesset.agendas.forms import (VoteLinkingForm, VoteLinkingFormSet,
                                   MeetingLinkingFormSet)
from django.core.cache import cache

register = template.Library()

@register.inclusion_tag('agendas/agendasfor.html')
def agendas_for(user, obj, object_type):
    ''' renders the relevent agenda for the object obj and a form for the
        agendas the given user can edit
    '''
    editable = []
    if user.is_authenticated():
        for a in user.agendas.all():
            r = {'agenda_name': a.name, 'agenda_id': a.id, 'obj_id': obj.id}
            try:
                av = None
                if object_type=='vote':
                    av = a.agendavotes.get(vote=obj)
                if object_type=='committeemeeting':
                    av = a.agendameetings.get(meeting=obj)
                if not av:
                    raise AgendaVote.DoesNotExist
                r['weight'] = av.score
                r['reasoning'] = av.reasoning
                r['object_type'] = object_type
                try:
                    r['importance'] = av.importance
                except AttributeError:
                    pass
            except (AgendaVote.DoesNotExist, AgendaMeeting.DoesNotExist):
                r['weight'] = None
                r['reasoning'] = u''
                r['object_type'] = object_type
            editable.append(r)

    av = None
    suggest_agendas = None
    suggested_agendas = None
    if object_type=='vote':
        av = AgendaVote.objects.filter(
                agenda__in=Agenda.objects.get_relevant_for_user(user),
                vote=obj).distinct()
        suggest_agendas = Agenda.objects.get_possible_to_suggest(
                user=user,
                vote=obj)
        if user.is_authenticated():
            suggested_agendas = UserSuggestedVote.objects.filter(user=user,
                                                                 vote=obj)
    if object_type=='committeemeeting':
        suggest_agendas = False
        av = AgendaMeeting.objects.filter(
                agenda__in=Agenda.objects.get_relevant_for_user(user),
                meeting=obj).distinct()
    if object_type=='bill':
        suggest_agendas = False
        av = AgendaBill.objects.filter(
                agenda__in=Agenda.objects.get_relevant_for_user(user),
                bill=obj).distinct()
    formset = None
    if editable:
        if object_type=='vote':
            formset = VoteLinkingFormSet(initial = editable)
        if object_type=='committeemeeting':
            formset = MeetingLinkingFormSet(initial = editable)
    return { 'formset': formset,
             'agendas':av,
             'object_type':object_type,
             'suggest_agendas': suggest_agendas,
             'suggested_agendas': suggested_agendas,
             'url':obj.get_absolute_url(),
           }

@register.inclusion_tag('agendas/agenda_list_item.html')
def agenda_list_item(agenda, watched_agendas=None, agenda_votes_num=None, agenda_party_values=None, parties_lookup=None, editors_lookup=None, editor_ids=None):

    #cached_context = cache.get('agenda_parties_%d' % agenda.id)
    #if not cached_context:
    #    selected_parties = agenda.selected_instances(Party, top=20,bottom=0)['top']
    #    cached_context = {'selected_parties': selected_parties }
    #    cache.set('agenda_parties_%d' % agenda.id, cached_context, 900)
    party_scores = [(parties_lookup[val[0]], val[1]) for val in agenda_party_values]
    enumerated_party = [(idx+0.5, values[0]) for idx, values in enumerate(party_scores)]
    enumerated_score = [(idx, values[1]) for idx, values in enumerate(party_scores)]
    return {'agenda': agenda,
            'watched_agendas': watched_agendas,
            'party_scores': json.dumps(enumerated_score, ensure_ascii=False),
            'party_list': json.dumps(enumerated_party, ensure_ascii=False),
            'agenda_votes_num': agenda_votes_num,
            'editors': editors_lookup,
            'editor_ids': editor_ids}
