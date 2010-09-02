from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
#from django.core.urlresolvers import reverse

from knesset.hashnav import DetailView, ListView, method_decorator
from knesset.laws.models import Vote

from forms import EditAgendaForm, AddAgendaForm
from models import Agenda, AgendaVote, score_text_to_score


class AgendaListView (ListView):
    def queryset(self):
        return Agenda.objects.all()
    
class AgendaDetailView (DetailView):
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
            agenda.description = form.cleaned_data['description']
            agenda.save()
#            return HttpResponseRedirect(reverse('agenda-detail',kwargs={'object_id':agenda.id}))
            return HttpResponseRedirect(agenda.get_absolute_url())
        else:
            self.form = form
            return HttpResponse(self.render_html()) #, mimetype=self.get_mimetype())

@login_required
def update_agendavote(request, agenda_id, vote_id):
    """
    Update agendavote relation for specific agenda-vote pair 
    """
    agenda = get_object_or_404(Agenda, pk=agenda_id)
    vote   = get_object_or_404(Vote, pk=vote_id)
    
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    if request.user not in agenda.editors.all():
        return HttpResponseForbidden("User %s does not have privileges to change agenda %s" % (request.user,agenda))

    try:
        action = request.POST['action']
    except KeyError:
        return HttpResponseForbidden("POST must have an 'action' attribute")
    
    if vote in agenda.votes.all():
        agendavote = agenda.agendavote_set.get(vote=vote) 

        if action=='remove':
            agendavote.delete()
            return HttpResponse("Agenda removed from vote")
        
        if action=='reasoning':
            agendavote.reasoning = request.POST['reasoning']
            agendavote.save()
            return HttpResponse("Agenda-vote updated with reasoning")
        
        if action in score_text_to_score.keys():
            agendavote.set_score_by_text(action)
            agendavote.save()
            return HttpResponse("Agenda-vote updated with '%s' score" % action)

        return HttpResponse("Action '%s' wasn't accepted" % action)
    
    else: # agenda is not ascribed to this vote
        if request.POST['action']=='ascribe':
            agenda_vote = AgendaVote(agenda=agenda,vote=vote,reasoning="")
            agenda_vote.save()
            return HttpResponse("Agenda ascribed to vote")

        return HttpResponse("Action '%s' wasn't accepted. You must ascribe the agenda before anything else." % action)

        
@login_required
def agenda_add_view(request):
    allowed_methods = ['GET', 'POST']
    template_name = 'agendas/agenda_add.html'
    
    if request.method == 'POST':
        form = AddAgendaForm(request.POST)
        if form.is_valid():
            agenda = Agenda()
            agenda.name = form.cleaned_data['name']
            agenda.description = form.cleaned_data['description']
            agenda.save()
            agenda.editors.add(request.user)
            return HttpResponseRedirect('/agenda/') # Redirect after POST
    else:
        form = AddAgendaForm() # An unbound form

    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))
