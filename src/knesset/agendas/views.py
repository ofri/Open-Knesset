import logging
from operator import itemgetter
from itertools import chain

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse
from django.core.cache import cache

from knesset.hashnav import DetailView, ListView, method_decorator
from knesset.laws.models import Vote
from knesset.mks.models import Member, Party
from knesset.api.urls import vote_handler

from forms import (EditAgendaForm, AddAgendaForm, VoteLinkingFormSet,
                   MeetingLinkingFormSet)
from models import Agenda, AgendaVote, AgendaMeeting

from queries import getAllAgendaPartyVotes, getAgendaEditorIds

from django.test import Client
from django.core.handlers.wsgi import WSGIRequest
from django.core.cache import cache

logger = logging.getLogger("open-knesset.agendas.views")

class AgendaListView (ListView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Agenda.objects.get_relevant_for_user(user=None)
        else:
            return Agenda.objects.get_relevant_for_user(user=self.request.user)

    def get_context(self, *args, **kwargs):
        context = super(AgendaListView, self).get_context(*args, **kwargs)
        # optimization - create query for votes per agenda
        # store in context as dictionary votes[agendaid]=<votenum> 
        agenda_votes_results = Agenda.objects.values("id").annotate(Count("votes"))
        agenda_votes = dict(map(lambda vote:(vote["id"],str(vote["votes__count"])),agenda_votes_results))
        allAgendaPartyVotes = cache.get('AllAgendaPartyVotes')
        if not allAgendaPartyVotes:
            allAgendaPartyVotes = getAllAgendaPartyVotes()
            cache.set('AllAgendaPartyVotes',allAgendaPartyVotes,1800)
        parties_lookup = dict(map(lambda party:(party.id,party.name),Party.objects.all()))
        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = p.agendas
        else:
            watched = None
        agendaEditorIds = getAgendaEditorIds()
        allEditorIds = list(set(chain.from_iterable(agendaEditorIds.values())))
        editors = User.objects.filter(id__in=allEditorIds)
        context['agenda_editors'] = agendaEditorIds
        context['editors'] = dict(map(lambda obj:(obj.id,obj),editors))
        context['watched'] = watched
        context['agenda_votes']=agenda_votes
        context['agenda_party_values']=allAgendaPartyVotes
        context['parties_lookup']=parties_lookup
        return context

class AgendaDetailView (DetailView):
    model = Agenda
    class ForbiddenAgenda(Exception):
        pass

    def get(self, request, *arg, **kwargs):
        try:
            response = super(AgendaDetailView, self).get(request, *arg, **kwargs)
        except self.ForbiddenAgenda:
            return HttpResponseForbidden()
        return response

    def get_object(self):
        obj = super(AgendaDetailView, self).get_object()
        if obj in Agenda.objects.get_relevant_for_user(user=self.request.user):
            return obj
        else:
            raise self.ForbiddenAgenda

    def get_context_data(self, *args, **kwargs):
        context = super(AgendaDetailView, self).get_context_data(*args, **kwargs)
        agenda = context['object']
        try:
            context['title'] = "%s" % agenda.name
        except AttributeError:
            context['title'] = _('None')

        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = agenda in p.agendas
            watched_members = self.request.user.get_profile().members
        else:
            watched = False
            watched_members = False
        context.update({'watched_object': watched})
        context['watched_members'] = watched_members

        all_mks = 'all_mks' in self.request.GET.keys()
        mks_values = agenda.get_mks_values()
        context['agenda_mk_values'] = dict(mks_values)
        cmp_rank = lambda x,y: x[1]['rank']-y[1]['rank']
        if all_mks:
            context['all_mks_ids'] = map(itemgetter(0),mks_values[:200])
            context['all_mks'] = True
        else:
            context['mks_top'] = map(itemgetter(0),mks_values[:5])
            context['mks_bottom'] = map(itemgetter(0),mks_values[-5:])

        allAgendaPartyVotes = cache.get('AllAgendaPartyVotes')
        if not allAgendaPartyVotes:
            allAgendaPartyVotes = getAllAgendaPartyVotes()
            cache.set('AllAgendaPartyVotes',allAgendaPartyVotes,1800)
        context['agenda_party_values']=dict(allAgendaPartyVotes.setdefault(agenda.id,[]))
        context['agendaTopParties']=map(itemgetter(0),sorted(allAgendaPartyVotes[agenda.id],key=itemgetter(1),reverse=True)[:20])

        cached_context = cache.get('agenda_votes_%d' % agenda.id)
        if not cached_context:
            agenda_votes = agenda.agendavotes.order_by('-vote__time')\
                                             .select_related('vote')
            cached_context = {'agenda_votes': agenda_votes }
            cache.set('agenda_votes_%d' % agenda.id, cached_context, 900)
        context.update(cached_context)

        # Optimization: get all parties and members before rendering
        # Further possible optimization: only bring parties/members needed for rendering
        parties_objects = Party.objects.all()
        partiesDict = dict(map(lambda party:(party.id,party),parties_objects))
        context['parties']=partiesDict

        member_objects = Member.objects.all()
        membersDict = dict(map(lambda mk:(mk.id,mk),member_objects))
        context['members']=membersDict
        return context

class AgendaMkDetailView (DetailView):
    model = Agenda
    template_name = 'agendas/mk_agenda_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AgendaMkDetailView, self).get_context_data(*args, **kwargs)
        agenda = context['object']
        context['agenda_url'] = agenda.get_absolute_url()
        context['agenda_name'] = agenda.name
        member =  Member.objects.get(pk=context['member_id'])
        context['member'] = member
        context['member_url'] = member.get_absolute_url()
        context['score'] = agenda.member_score(member)

        try:
            context['title'] = _("Analysis of %(member)s votes by agenda %(agenda)s") % {'member':member.name, 'agenda':agenda.name}
        except AttributeError:
            context['title'] = _('None')
            logger.error('Attribute error trying to generate title for agenda %d member %d' % (self.object_id,self.member_id))

        related_mk_votes = agenda.related_mk_votes(member)

        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = agenda in p.agendas
        else:
            watched = False

        context.update({'watched_object': watched})
        context.update({'related_votes': related_mk_votes})

        return context

class AgendaDetailEditView (DetailView):
    model = Agenda
    template_name = 'agendas/agenda_detail_edit.html'

    def get(self, request, *args, **kwargs):
        object_id = kwargs.get('pk' , kwargs.get('object_id', None))
        agenda = get_object_or_404(Agenda, pk=object_id)
        if request.user in agenda.editors.all():
            return super(AgendaDetailEditView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(agenda.get_absolute_url())

    def get_context_data(self, *args, **kwargs):
        context = super(AgendaDetailEditView, self).get_context_data(*args, **kwargs)
        agenda = context['object']
        form = getattr (self, 'form', None)
        if form is None:
            form = EditAgendaForm(agenda=agenda if self.request.method == 'GET' else None)
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        object_id = kwargs.get('pk' , kwargs.get('object_id', None))
        agenda = get_object_or_404(Agenda, pk=object_id)
        if request.user not in agenda.editors.all():
            return HttpResponseForbidden()
        form = EditAgendaForm(data=self.request.POST)
        if form.is_valid(): # All validation rules pass
            agenda.name = form.cleaned_data['name']
            agenda.public_owner_name = form.cleaned_data['public_owner_name']
            agenda.description = form.cleaned_data['description']
            agenda.save()
#            return HttpResponseRedirect(reverse('agenda-detail',kwargs={'object_id':agenda.id}))
            return HttpResponseRedirect(agenda.get_absolute_url())
        else:
            self.form = form
            return super(AgendaDetailEditView, self).get(request, *args, **kwargs)

class MockApiCaller(Client):
    def get_vote_api(self,vote):
        return vote_handler( self.get('/api/vote/%d/' % vote.id) )  # TODO: get the url from somewhere else?

    def request(self, **request):
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)

mock_api = MockApiCaller()

@login_required
def agenda_add_view(request):
    allowed_methods = ['GET', 'POST']
    template_name = 'agendas/agenda_add.html'

    if not request.user.is_superuser:
        return HttpResponseRedirect('/agenda/')

    if request.method == 'POST':
        form = AddAgendaForm(request.POST)
        if form.is_valid():
            agenda = Agenda()
            agenda.name = form.cleaned_data['name']
            agenda.public_owner_name = form.cleaned_data['public_owner_name']
            agenda.description = form.cleaned_data['description']
            agenda.save()
            agenda.editors.add(request.user)
            return HttpResponseRedirect('/agenda/') # Redirect after POST
    else:
        initial_data = {'public_owner_name': request.user.username}
        form = AddAgendaForm(initial=initial_data) # An unbound form with initial data

    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))

@login_required
def update_editors_agendas(request):
    if request.method == 'POST':
        object_type = request.POST.get('form-0-object_type',None)
        object_id = request.POST.get('form-0-vote_id',None)
        if object_type=='vote':
            vl_formset = VoteLinkingFormSet(request.POST)
        else:
            vl_formset = MeetingLinkingFormSet(request.POST)
        if vl_formset.is_valid():
            for a in vl_formset.cleaned_data:
                if a:
                    # Check that the user is an editor of the agenda
                    # he's trying to edit
                    try:
                        agenda = Agenda.objects.get(pk=a['agenda_id'])
                        if request.user not in agenda.editors.all():
                            return HttpResponseForbidden()
                    except Agenda.DoesNotExist:
                        return HttpResponseForbidden()

                    if a['object_type'] == 'vote':
                        if a['DELETE']:
                            try:
                                object_id = a['vote_id']
                                av = AgendaVote.objects.get(
                                       agenda__id=a['agenda_id'],
                                       vote__id = a['vote_id'])
                                av.delete()
                            except AgendaVote.DoesNotExist:
                                pass
                        else: # not delete, so try to create
                            if (a['weight'] is not '' and
                                a['importance'] is not ''):
                                try:
                                    object_id = a['vote_id']
                                    av = AgendaVote.objects.get(
                                           agenda__id=a['agenda_id'],
                                           vote__id = a['vote_id'])
                                    av.score = a['weight']
                                    av.importance = a['importance']
                                    av.reasoning = a['reasoning']
                                    av.save()
                                except AgendaVote.DoesNotExist:
                                    av = AgendaVote(
                                           agenda_id=int(a['agenda_id']),
                                           vote_id=int(a['vote_id']),
                                           score = a['weight'],
                                           importance = a['importance'],
                                           reasoning = a['reasoning'])
                                    av.save()
                    if a['object_type'] == 'committeemeeting':
                        if a['DELETE']:
                            try:
                                object_id = a['vote_id']
                                av = AgendaMeeting.objects.get(
                                       agenda__id=a['agenda_id'],
                                       meeting__id = a['vote_id'])
                                av.delete()
                            except AgendaMeeting.DoesNotExist:
                                pass
                        else: # not delete, so try to create
                            try:
                                object_id = a['vote_id']
                                av = AgendaMeeting.objects.get(
                                       agenda__id=a['agenda_id'],
                                       meeting__id = a['vote_id'])
                                av.score = a['weight']
                                av.reasoning = a['reasoning']
                                av.save()
                            except AgendaMeeting.DoesNotExist:
                                av = AgendaMeeting(
                                       agenda_id=int(a['agenda_id']),
                                       meeting_id=int(a['vote_id']),
                                       score = a['weight'],
                                       reasoning = a['reasoning'])
                                av.save()
                else:
                    logger.info("invalid form")

        else:
            # TODO: Error handling: what to do with illeal forms?
            logger.info("invalid formset")
            logger.info("%s" % vl_formset.errors)
        if object_id:
            if object_type=='vote':
                return HttpResponseRedirect(reverse('vote-detail',
                                        kwargs={'object_id':object_id}))
            else:
                return HttpResponseRedirect(reverse('committee-meeting',
                                         kwargs={'pk':object_id}))
        else: # no object id was found, return to list
            if object_type=='vote':
                return HttpResponseRedirect(reverse('vote-list'))
            else:
                return HttpResponseRedirect(reverse('committee-list'))

    else:
        return HttpResponseNotAllowed(['POST'])
