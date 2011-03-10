from django.utils.translation import ugettext as _
from django.http import Http404
from knesset.hashnav import ListView, DetailView
from knesset.persons.models import Person
from knesset.committees.models import CommitteeMeeting

class PersonListView(ListView):

    def get_context(self):
        context = super(PersonListView, self).get_context()
        if not self.items:
            raise Http404
        context['title'] = _('Persons in committee meetings')
        return context 

    def get_queryset (self):
        return Person.objects.filter(protocol_parts__isnull=False).distinct()
        
class PersonDetailView(DetailView):
    def get_context(self, *args, **kwargs):
        context = super(PersonDetailView, self).get_context(*args, **kwargs)
        person = context['object']
        context['title'] = _('%(name)s in committee meetings') % {'name':person.name} 
        context['meetings'] = CommitteeMeeting.objects.filter(id__in=[m['meeting'] for m in person.protocol_parts.values('meeting').distinct()])
        return context  