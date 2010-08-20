from knesset.hashnav import DetailView, ListView, method_decorator
from django.utils.translation import ugettext_lazy as _

class AgendaListView (ListView):
    pass
    
    
class AgendaDetailView (DetailView):
    def get_context(self, *args, **kwargs):
        context = super(AgendaDetailView, self).get_context(*args, **kwargs)       
        agenda = context['object']
        try:
            context['title'] = "%s" % agenda.name
        except AttributeError:
            context['title'] = _('None')
        return context

