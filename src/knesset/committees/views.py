from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import logging 
logger = logging.getLogger("open-knesset.committees.views")
import difflib
import datetime
import re

from knesset.hashnav import ListView, DetailView
from knesset.laws.models import Bill, PrivateProposal
from models import *

class MeetingDetailView(DetailView):

    allowed_methods = ['GET', 'POST'],

    @login_required
    def POST(self, object_id, **kwargs):
        bill = None
        request = self.request
        try:
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
                cm.save() # just to signal, so the attended Action gets created.
                action.send(request.user, verb='merged',
                    description=cm,
                    target=mk,
                    timestamp=datetime.datetime.now())

        except Exception,e:
            logger.error(e)
        
        return HttpResponseRedirect(".")

class MeetingsListView(ListView):

    def get_context(self, *args, **kwargs):
        context = super(MeetingsListView, self).get_context(*args, **kwargs)
        context['title'] = _('All meetings by %(committee)s') % {'committee':self.items[0].committee.name}
        return context 

    def get_queryset (self, **kwargs):
        if 'committee_id' in kwargs:
            return CommitteeMeeting.objects.filter(committee__id=kwargs['committee_id'])
        else:
            return CommitteeMeeting.objects.all()
        
