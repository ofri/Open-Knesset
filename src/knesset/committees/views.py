from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
import logging 
logger = logging.getLogger("open-knesset.committees.views")
import difflib
import datetime
import re

from knesset.hashnav.views import ListDetailView
from knesset.laws.models import Bill, PrivateProposal
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

    def handle_post(self, request, object_id, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(".")            

        bill = None
        try:
            cm = CommitteeMeeting.objects.get(pk=object_id)
            user_input_type = request.POST.get('user_input_type')
            if user_input_type == 'bill':
                bill_id = request.POST.get('bill_id')
                if bill_id.isdigit(): 
                    bill = Bill.objects.get(pk=bill_id)
                else: # not a number, maybe its p/1234
                    m = re.findall('\d+',bill_id)
                    if len(m)!=1:
                        raise ValueError("didn't find exactly 1 number in bill_id=%s" % bill_id)
                    pp = PrivateProposal.objects.get(proposal_id=m[0])
                    bill = pp.bill                    
                
                if bill.stage in ['1','2','-2','3']: # this bill is in early stage, so cm must be one of the first meetings
                    bill.first_committee_meetings.add(cm)
                else: # this bill is in later stages
                    v = bill.first_vote # look for first vote
                    if v and v.time.date() < cm.date: # and check if the cm is after it,            
                        bill.second_committee_meetings.add(cm) # if so, this is a second committee meeting
                    else: # otherwise, assume its first cms.
                        bill.first_committee_meetings.add(cm)
                bill.update_stage()
                action.send(request.user, verb='merged',
                    description=cm,
                    target=bill,
                    timestamp=datetime.datetime.now())
                
            if user_input_type == 'mk':
                mk_names = Member.objects.values_list('name',flat=True)
                mk_name = difflib.get_close_matches(request.POST.get('mk_name'), mk_names)[0]
                mk = Member.objects.get(name=mk_name)
                cm.mks_attended.add(mk)
                action.send(request.user, verb='merged',
                    description=cm,
                    target=mk,
                    timestamp=datetime.datetime.now())

        except Exception,e:
            logger.error(e)
        
        return HttpResponseRedirect(".")

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
        
