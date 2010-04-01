from django.utils.translation import ugettext as _

from knesset.hashnav.views import ListDetailView
from models import *

class CommitteesView(ListDetailView):

    def render_object(self, request, object_id, **kwargs):
        if not self.extra_context: self.extra_context = {}
        self.extra_context['meetings_list'] = CommitteeMeeting.objects.filter(committee__pk=object_id)[:10]
        return super(CommitteesView, self).render_object(request, object_id, **kwargs)

class CommitteeMeetingView(ListDetailView):

    def render_object(self,request, object_id=None,**kwargs):
        if not self.extra_context: self.extra_context = {}
        cm = CommitteeMeeting.objects.get(pk=object_id)
        self.extra_context['title'] = _('%(committee)s meeting on %(date)s') % {'committee':cm.committee.name, 'date':cm.date_string}
        return super(CommitteeMeetingView, self).render_object(request, object_id, **kwargs)

    def render_list(self, request, committee_id=None, **kwargs):
        if not self.extra_context: self.extra_context = {}
        c = Committee.objects.get(pk=committee_id)      
        self.extra_context['title'] = _('All meetings by %(committee)s') % {'committee':c.name}
        return super(CommitteeMeetingView, self).render_list(request, **kwargs)

    def pre (self, request, **kwargs):
        if 'committee_id' in kwargs:            
            self.queryset = CommitteeMeeting.objects.filter(committee__id=kwargs['committee_id'])
        else:
            self.queryset = CommitteeMeeting.objects.all()
        
