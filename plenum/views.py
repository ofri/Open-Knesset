from committees.views import *
from committees.models import *

class PlenumView(CommitteeDetailView):    
    
    def get_object(self, *args, **kwargs):
        return Committee.objects.get(type='plenum')
    
class PlenumMeetingsListView(MeetingsListView):
    
    def get_queryset (self):
        c_id = Committee.objects.get(type='plenum').id
        if c_id:
            return CommitteeMeeting.objects.filter(committee__id=c_id)
        else:
            return CommitteeMeeting.objects.all()
        
    def get_context(self):
        context = super(PlenumMeetingsListView, self).get_context()
        context['committee_type'] = 'plenum'
        return context
    
class PlenumMeetingDetailView(MeetingDetailView):
    
    def get_context_data(self, *args, **kwargs):
        context=super(PlenumMeetingDetailView, self).get_context_data(*args, **kwargs)
        context['parts']=context['object'].parts.filter(type='title')
        context['is_titles_only']=True
        return context