from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _
from django.utils import simplejson as json
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404,render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import RequestContext
import logging
import difflib
import datetime
import re
import colorsys
from tagging.models import TaggedItem
from tagging.utils import get_tag
from actstream import action
from knesset.hashnav import ListView, DetailView, method_decorator
from knesset.laws.models import Bill, PrivateProposal
from knesset.mks.models import Member
from knesset.events.models import Event
from knesset.utils import clean_string
from models import Committee, CommitteeMeeting, Topic, COMMITTEE_PROTOCOL_PAGINATE_BY

logger = logging.getLogger("open-knesset.committees.views")

committees_list = ListView(queryset = Committee.objects.all(), paginate_by=20)

class CommitteeListView(generic.ListView):
    context_object_name = 'committees'
    model = Committee
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(CommitteeListView, self).get_context_data(**kwargs)
        context["topics"] = Topic.objects.get_public()[:10]
        context["rating_range"] = range(7)
        return context

class CommitteeDetailView(DetailView):

    model = Committee

    def get_context_data(self, *args, **kwargs):
        context = super(CommitteeDetailView, self).get_context_data(*args, **kwargs)
        cm = context['object']

        context['chairpersons'] = cm.chairpersons.all()
        context['replacements'] = cm.replacements.all()
        context['members'] = cm.members_by_presence()
        recent_meetings = cm.recent_meetings()
        context['meetings_list'] = recent_meetings
        ref_date = recent_meetings[0].date+datetime.timedelta(1) \
                if recent_meetings.count() > 0 \
                else datetime.datetime.now()
        cur_date = datetime.datetime.now()
        context['future_meetings_list'] = cm.events.filter(when__gt = cur_date)
        context['protocol_not_yet_published_list'] = cm.events.filter(when__gt = ref_date, when__lte = cur_date)
        context['annotations'] = cm.annotations.order_by('-timestamp')
        context['topics'] = cm.get_public_topics()
        return context

class MeetingDetailView(DetailView):

    model = CommitteeMeeting

    def get_context_data(self, *args, **kwargs):
        context = super(MeetingDetailView, self).get_context_data(*args, **kwargs)
        cm = context['object']
        colors = {}
        speakers = cm.parts.order_by('speaker__mk').values_list('header','speaker__mk').distinct()
        n = speakers.count()
        for (i,(p,mk)) in enumerate(speakers):
            (r,g,b) = colorsys.hsv_to_rgb(float(i)/n, 0.5 if mk else 0.3, 255)
            colors[p] = 'rgb(%i, %i, %i)' % (r, g, b)
        context['title'] = _('%(committee)s meeting on %(date)s') % {'committee':cm.committee.name, 'date':cm.date_string}
        context['description'] = _('%(committee)s meeting on %(date)s on topic %(topic)s') \
                                   % {'committee':cm.committee.name,
                                      'date':cm.date_string,
                                      'topic':cm.topics}
        context['description'] = clean_string(context['description']).replace('"','')
        page = self.request.GET.get('page',None)
        if page:
            context['description'] += _(' page %(page)s') % {'page':page}
        context['colors'] = colors
        parts_lengths = {}
        for part in cm.parts.all():
            parts_lengths[part.id] = len(part.body)
        context['parts_lengths'] = json.dumps(parts_lengths)
        context['paginate_by'] = COMMITTEE_PROTOCOL_PAGINATE_BY
        return context


    @method_decorator(login_required)
    def post(self, request, **kwargs):
        cm = get_object_or_404(CommitteeMeeting, pk=kwargs['pk'])
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

class TopicListView(generic.ListView):
    model = Topic
    context_object_name = 'topics'

    def get_queryset(self):
        qs = Topic.objects.get_public()
        if "committee_id" in self.kwargs:
            qs = qs.filter(committees__id=self.kwargs["committee_id"])
        return qs

    def get_context_data(self, **kwargs):
        context = super(TopicListView, self).get_context_data(**kwargs)
        committee_id = self.kwargs.get("committee_id", False)
        context["committee"] = committee_id and Committee.objects.get(pk=committee_id)
        return context

class TopicDetailView(DetailView):
    model = Topic
    context_object_name = 'topic'
    def get_context_data(self, **kwargs):
        context = super(TopicDetailView, self).get_context_data(**kwargs)
        topic = context['object']
        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = topic in p.topics
        else:
            watched = False
        context['watched_object'] = watched
        return context



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

def meeting_tag(request, tag):
    tag_instance = get_tag(tag)
    if tag_instance is None:
        raise Http404(_('No Tag found matching "%s".') % tag)

    extra_context = {'tag':tag_instance}
    extra_context['tag_url'] = reverse('committeemeeting-tag',args=[tag_instance])
    extra_context['title'] = ugettext_lazy('Committee Meetings tagged %(tag)s') % {'tag': tag}
    qs = CommitteeMeeting
    queryset = TaggedItem.objects.get_by_model(qs, tag_instance)
    return generic.list_view.object_list(request, queryset,
        template_name='committees/committeemeeting_list_by_tag.html', extra_context=extra_context)

def delete_topic_rating(request, object_id):
    if request.method=='POST':
        topic= get_object_or_404(Topic, pk=object_id)
        topic.rating.delete(request.user, request.META['REMOTE_ADDR'])
        return HttpResponse('Vote deleted.')



