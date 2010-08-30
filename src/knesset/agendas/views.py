from knesset.hashnav import DetailView, ListView, method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from forms import EditAgendaForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from knesset.laws.models import Vote
from models import Agenda, AgendaVote
#from django.core.urlresolvers import reverse

class AgendaListView (ListView):
    def queryset(self):
        return Agendas.objects.all()
    
class AgendaDetailView (DetailView):
    def get_context(self, *args, **kwargs):
        context = super(AgendaDetailView, self).get_context(*args, **kwargs)       
        agenda = context['object']
        try:
            context['title'] = "%s" % agenda.name
        except AttributeError:
            context['title'] = _('None')
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
    
    if request.method == 'POST':
        if request.user not in agenda.editors.all():
            HttpResponse("This is not the correct user")
        if vote not in agenda.votes.all():
            if request.POST['action']=='ascribe':
                agenda_vote = AgendaVote(agenda=agenda,vote=vote,reasoning="")
                agenda_vote.save()
                return HttpResponse("Agenda ascribed to vote")
            else:
                return HttpResponse("You must ascribe the agenda before anything else")
        else: # Agenda already ascribed to the vote
            agendavote = agenda.agendavote_set.get(vote=vote) 
            if request.POST['action']=='remove':
                agendavote.delete()
                return HttpResponse("Agenda removed from vote")
            
            if request.POST['action']=='reasoning':
                agendavote.reasoning = request.POST['reasoning']
                agendavote.save()
                return HttpResponse("Agenda-vote updated with reasoning")
            
            agendavote.set_score_by_text(request.POST['action'])
            agendavote.save()
            return HttpResponse("Agenda-vote updated with %s score" % request.POST['action'])
    else:
        return HttpResponse("Only POST allowed")
        

