from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404,render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import logging 
from django.contrib.contenttypes.models import ContentType
import difflib
import datetime
import re
import colorsys
from actstream import action
from knesset.hashnav import ListView, DetailView, method_decorator
from knesset.laws.models import Bill, PrivateProposal
from knesset.mks.models import Member
from knesset.events.models import Event 
from models import Committee, CommitteeMeeting, COMMITTEE_PROTOCOL_PAGINATE_BY

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("Need a json decoder")

logger = logging.getLogger("open-knesset.committees.views")


class CommitteeDetailView(DetailView):

    allowed_methods = ('GET', )

    def get_context(self, *args, **kwargs):       
        context = super(CommitteeDetailView, self).get_context(*args, **kwargs)
        cm = context['object']  
        
        def annotate_members(qs):
            members = []
            for m in qs:
                m.meetings_count = (100 * m.committee_meetings.filter(committee=cm).count()) / cm.meetings.count()
                members.append(m)
            members.sort(key=lambda x:x.meetings_count, reverse=True)
            return members

        context['chairpersons'] = cm.chairpersons.all()
        context['replacements'] = cm.replacements.all()
        context['members'] = annotate_members(\
            (cm.members.all()|context['chairpersons']|context['replacements']).distinct())
        recent_meetings = cm.meetings.all().order_by('-date')[:10]
        context['meetings_list'] = recent_meetings
        ref_date = recent_meetings[0].date if recent_meetings.count() > 0 else datetime.datetime.now()
        cur_date = datetime.datetime.now()
        context['future_meetings_list'] = cm.events.filter(when__gt = cur_date)
        context['protocol_not_yet_published_list'] = cm.events.filter(when__gt = ref_date, when__lte = cur_date)
        context['annotations'] = cm.annotations.order_by('-timestamp')
        return context 

class MeetingDetailView(DetailView):

    allowed_methods = ('GET', 'POST')

    def get_context(self, *args, **kwargs):
        context = super(MeetingDetailView, self).get_context(*args, **kwargs)  
        cm = context['object']
        colors = {}
        speakers = cm.parts.order_by('speaker__mk').values_list('header','speaker__mk').distinct()
        n = speakers.count()
        for (i,(p,mk)) in enumerate(speakers):
            (r,g,b) = colorsys.hsv_to_rgb(float(i)/n, 0.5 if mk else 0.3, 255)
            colors[p] = 'rgb(%i, %i, %i)' % (r, g, b)
        context['title'] = _('%(committee)s meeting on %(date)s') % {'committee':cm.committee.name, 'date':cm.date_string}
        context['colors'] = colors
        parts_lengths = {}
        for part in cm.parts.all():
            parts_lengths[part.id] = len(part.body)
        context['parts_lengths'] = json.dumps(parts_lengths)
        context['paginate_by'] = COMMITTEE_PROTOCOL_PAGINATE_BY
        return context 


    @method_decorator(login_required)
    def POST(self, object_id, **kwargs):
        cm = get_object_or_404(CommitteeMeeting, pk=object_id)
        bill = None
        request = self.request
        user_input_type = request.POST.get('user_input_type')
        if user_input_type == 'bill':
            bill_id = request.POST.get('bill_id')
            if bill_id.isdigit():
                bill = get_object_or_404(Bill, pk=bill_id)
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
                if v and v.time.date() < cm.date:          # and check if the cm is after it,
                    bill.second_committee_meetings.add(cm) # if so, this is a second committee meeting
                else: # otherwise, assume its first cms.
                    bill.first_committee_meetings.add(cm)
            bill.update_stage()
            action.send(request.user, verb='added-bill-to-cm',
                description=cm,
                target=bill,
                timestamp=datetime.datetime.now())

        if user_input_type == 'mk':
            mk_names = Member.objects.values_list('name',flat=True)
            mk_name = difflib.get_close_matches(request.POST.get('mk_name'), mk_names)[0]
            mk = Member.objects.get(name=mk_name)
            cm.mks_attended.add(mk)
            cm.save() # just to signal, so the attended Action gets created.
            action.send(request.user, verb='added-mk-to-cm',
                description=cm,
                target=mk,
                timestamp=datetime.datetime.now())

        return HttpResponseRedirect(".")
_('added-bill-to-cm')
_('added-mk-to-cm')

class MeetingsListView(ListView):

    def get_context(self):
        context = super(MeetingsListView, self).get_context()
        if not self.items:
            raise Http404
        context['title'] = _('All meetings by %(committee)s') % {'committee':self.items[0].committee.name}
        context['none'] = _('No %(object_type)s found') % {'object_type': CommitteeMeeting._meta.verbose_name_plural }
        context['committee_id'] = self.committee_id
        return context 

    def get_queryset (self):
        c_id = getattr(self, 'committee_id', None)
        if c_id:
            return CommitteeMeeting.objects.filter(committee__id=c_id)
        else:
            return CommitteeMeeting.objects.all()
        
def meeting_list_by_date(request, *args, **kwargs):
    committee_id = kwargs.get('committee_id',None)
    date_string = kwargs.get('date',None)
    try:
        date = datetime.datetime.strptime(date_string,'%Y-%m-%d').date()
    except:
        raise Http404()
    object = get_object_or_404(Committee, pk=committee_id)
    object_list = object.meetings.filter(date=date)
    
    context = {'object_list':object_list, 'committee_id':committee_id}
    context['title'] = _('Meetings by %(committee)s on date %(date)s') % {'committee':object.name, 'date':date}
    context['none'] = _('No %(object_type)s found') % {'object_type': CommitteeMeeting._meta.verbose_name_plural } 
    return render_to_response("committees/committeemeeting_list.html",
        context, context_instance=RequestContext(request))    
