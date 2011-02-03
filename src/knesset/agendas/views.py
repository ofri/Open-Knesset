from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse

from knesset.hashnav import DetailView, ListView, method_decorator
from knesset.laws.models import Vote
from knesset.mks.models import Member, Party
from knesset.api.urls import vote_handler

from forms import EditAgendaForm, AddAgendaForm, VoteLinkingFormSet
from models import Agenda, AgendaVote

from django.test import Client
from django.core.handlers.wsgi import WSGIRequest

class AgendaListView (ListView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Agenda.objects.get_relevant_for_user(user=None)
        else:
            return Agenda.objects.get_relevant_for_user(user=self.request.user)
    
    def get_context(self, *args, **kwargs):
        context = super(AgendaListView, self).get_context(*args, **kwargs)       
        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = p.agendas
        else:
            watched = None
        context['watched'] = watched
        return context
        
class AgendaDetailView (DetailView):
    class ForbiddenAgenda(Exception):
        pass
    
    queryset = Agenda.objects.all()
    
    def GET(self, *arg, **kwargs):
        try:
            response = super(AgendaDetailView, self).GET(*arg, **kwargs)
        except self.ForbiddenAgenda:
            return HttpResponseForbidden()
        return response
        
    def get_object(self):
        obj = super(AgendaDetailView, self).get_object()
        if obj in Agenda.objects.get_relevant_for_user(user=self.request.user):
            return obj
        else:
            raise self.ForbiddenAgenda
        
    def get_context(self, *args, **kwargs):
        context = super(AgendaDetailView, self).get_context(*args, **kwargs)       
        agenda = context['object']
        try:
            context['title'] = "%s" % agenda.name
        except AttributeError:
            context['title'] = _('None')

        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = agenda in p.agendas
        else:
            watched = False
        
        context.update({'watched_object': watched})
        
        selected_mks = agenda.selected_instances(Member, top=3,bottom=3)
        selected_mks = selected_mks['top']+selected_mks['bottom']
        selected_parties = agenda.selected_instances(Party, top=3,bottom=3)
        selected_parties = selected_parties['top']+selected_parties['bottom']
        context.update({'selected_mks': selected_mks })
        context.update({'selected_parties': selected_parties })
        
        return context
    
class AgendaMkDetailView (DetailView):
    template_name = 'agendas/mk_agenda_detail.html'
    
    def get_queryset(self):
        return Agenda.objects.get_specific(agendaId=self.object_id)

    def get_context(self, *args, **kwargs):
        context = super(AgendaMkDetailView, self).get_context(*args, **kwargs)       
        agenda = context['object']
        try:
            context['title'] = "%s" % agenda.name
        except AttributeError:
            context['title'] = _('None')

        viewed_mk =  Member.objects.get(pk=self.member_id)
        context['member'] = viewed_mk
        related_mk_votes = agenda.related_mk_votes(viewed_mk)
        
        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = agenda in p.agendas
        else:
            watched = False
        
        context.update({'watched_object': watched})
        context.update({'related_votes': related_mk_votes})
        
        return context

class AgendaDetailEditView (DetailView):
    allowed_methods = ['GET', 'POST']
    template_name = 'agendas/agenda_detail_edit.html'

    def __call__(self, request, *args, **kwargs):
        agenda = get_object_or_404(Agenda, pk=kwargs['object_id'])
        if request.user in agenda.editors.all():
            return super(AgendaDetailEditView, self).__call__(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(agenda.get_absolute_url())

    def get_context(self, *args, **kwargs):
        context = super(AgendaDetailEditView, self).get_context(*args, **kwargs)       
        agenda = context['object']
        form = getattr (self, 'form', None)
        if form is None:
            form = EditAgendaForm(agenda=agenda if self.request.method == 'GET' else None)
        context['form'] = form
        return context

    @method_decorator(login_required)
    def POST(self, object_id, **kwargs):
        form = EditAgendaForm(data=self.request.POST)
        if form.is_valid(): # All validation rules pass
            agenda = get_object_or_404(Agenda, pk=object_id)
            agenda.name = form.cleaned_data['name']
            agenda.public_owner_name = form.cleaned_data['public_owner_name']
            agenda.description = form.cleaned_data['description']
            agenda.save()
#            return HttpResponseRedirect(reverse('agenda-detail',kwargs={'object_id':agenda.id}))
            return HttpResponseRedirect(agenda.get_absolute_url())
        else:
            self.form = form
            return HttpResponse(self.render_html()) #, mimetype=self.get_mimetype())


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
        vl_formset = VoteLinkingFormSet(request.POST)
        if vl_formset.is_valid():
            # TODO: check the user's permission
            for a in vl_formset.cleaned_data:
                try:
                    av = AgendaVote.objects.get(
                           agenda__id=a['agenda_id'],
                           vote__id = a['vote_id'])
                    av.score = a['weight']
                    av.reasoning = a['reasoning']
                    av.save()
                except AgendaVote.DoesNotExist:
                    av = AgendaVote(
                           agenda_id=int(a['agenda_id']),
                           vote_id=int(a['vote_id']),
                           score = a['weight'],
                           reasoning = a['reasoning'])
                    av.save()
            return HttpResponseRedirect(reverse('vote-detail', kwargs={'object_id':a['vote_id']}))
        else:
            # TODO: Error handling: what to do with illeal forms?
            pass

    else:
        return HttpResponseNotAllowed(['POST'])
