#encoding: utf-8
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list, object_detail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext

from tagging.models import Tag, TaggedItem
from tagging.views import tagged_object_list
from actstream import action
from knesset.utils import limit_by_request
from knesset.laws.models import *
from knesset.tagvotes.models import TagVote
from knesset.hashnav.views import ListDetailView

import urllib
import urllib2
import difflib
import logging 
import datetime
logger = logging.getLogger("open-knesset.laws.views")

def bill_by_knesset_booklet(request, booklet_num):
    kps = KnessetProposal.objects.filter(booklet_number=booklet_num).values_list('id',flat=True)
    queryset = Bill.objects.filter(knesset_proposal__in=kps)
    context = {'title':'Bills published in knesset booklet number %s' % booklet_num ,
               'object_list': queryset}
    template_name = "laws/bill_list.html"
    c = RequestContext(request, context)
    t = loader.get_template(template_name)
    return HttpResponse(t.render(c))

class BillView (ListDetailView):

    def render_object(self, request, object_id, extra_context=None, **kwargs):
        if not extra_context:
            extra_context = {}
        bill = get_object_or_404(Bill, pk=object_id)
        extra_context['title'] = "%s %s" % (bill.law.title, bill.title)
        try:
            kp = bill.knesset_proposal
            t = kp.law.title + ' ' + kp.title
            vs = Vote.objects.values('title','id')
            vs_titles = [v['title'] for v in vs]
            close_votes = difflib.get_close_matches(t, vs_titles, cutoff=0.5)
            all_bill_votes = []
            all_bill_votes.extend(bill.pre_votes.values_list('id',flat=True))
            if bill.first_vote:
                all_bill_votes.append(bill.first_vote.id)
            if bill.approval_vote:
                all_bill_votes.append(bill.approval_vote.id)
            close_votes = [(v['id'],v['title']) for v in vs if v['title'] in close_votes and v['id'] not in all_bill_votes]
            extra_context['close_votes'] = close_votes
        except Exception, e:
            pass
        return super(BillView, self).render_object(request, object_id,
                              extra_context=extra_context, **kwargs)

    friend_pages = [
            ('stage','all',_('All stages')),
    ]
    friend_pages.extend([('stage',x[0],_(x[1])) for x in BILL_STAGE_CHOICES])

    def render_list(self, request, extra_context=None, **kwargs):
        stage_filter = request.GET.get('stage',None)
        r = [['?%s=%s'% (x[0],x[1]),x[2],False,x[1]] for x in self.friend_pages]
        if stage_filter and stage_filter!='all':
            queryset = self.queryset.filter(stage=stage_filter)
            for x in r:
                if x[3]==stage_filter:
                    x[2] = True
                    break
        else:
            queryset = self.queryset
            r[0][2] = True
        if not extra_context:
            extra_context = {}
        extra_context['friend_pages'] = r
        return super(BillView, self).render_list(request, queryset=queryset, extra_context=extra_context,**kwargs)

    
    def handle_post(self, request, object_id, extra_context=None, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(".")            
        vote = None
        try:
            bill = Bill.objects.get(pk=object_id)
            user_input_type = request.POST.get('user_input_type')
            if user_input_type == 'approval vote':            
                vote = Vote.objects.get(pk=request.POST.get('vote_id'))
                bill.approval_vote = vote
                bill.update_stage()
            if user_input_type == 'first vote':            
                vote = Vote.objects.get(pk=request.POST.get('vote_id'))
                bill.first_vote = vote
                bill.update_stage()
            if user_input_type == 'pre vote':            
                vote = Vote.objects.get(pk=request.POST.get('vote_id'))
                bill.pre_votes.add(vote)
                bill.update_stage()

            action.send(request.user, verb='merged',
                    description=vote,
                    target=bill,
                    timestamp=datetime.datetime.now())
        except Exception,e:
            logger.error(e)
        return HttpResponseRedirect(".")
        
class LawView (ListDetailView):

    def render_object(self, request, object_id, extra_context=None, **kwargs):
        if not extra_context:
            extra_context = {}
        law = Law.objects.get(pk=object_id)
        pps = PrivateProposal.objects.filter(law=law).annotate(c=Count('knesset_proposals')).filter(c=0).order_by('title')
        kps = KnessetProposal.objects.filter(law=law)
        extra_context['pps'] = pps
        extra_context['kps'] = kps
        extra_context['title'] = law.title
        return super(LawView, self).render_object(request, object_id,
                              extra_context=extra_context, **kwargs)       
        

class VoteListView(ListDetailView):

    session_votes_key = 'selected_votes'
    
    friend_pages = [
            ('vote_type','all',_('All votes')),
            ('vote_type','law-approve', _('Law Approvals')),
            ('vote_type','second-call', _('Second Call')),
            ('vote_type','demurrer', _('Demurrer')),
            ('vote_type','no-confidence', _('Motion of no confidence')),
            ('vote_type','pass-to-committee', _('Pass to committee')),
            ('vote_type','continuation', _('Continuation')),
            ('tagged','all',_('All')),
            ('tagged','false',_('Untagged Votes')),
            ('tagged','true',_('Tagged Votes')),            
            ('time','7',_('Last Week')),
            ('time','30',_('Last Month')),
            ('time','all',_('All times')),
            ('order','time',_('Time')),
            ('order','controversy', _('Controversy')),
            ('order','against-party',_('Against Party')),
            ('order','votes',_('Number of votes')),
            
        ]

    def pre (self, request, **kwargs):

        pass
        

    def render_list(self,request, **kwargs):

        
        if not self.extra_context: self.extra_context = {}

        saved_selection = request.session.get(self.session_votes_key, dict())
        options = {
            'type': request.GET.get('vote_type', saved_selection.get('vote_type', None)),
            'since': request.GET.get('time', saved_selection.get('time',None)),
            'order': request.GET.get('order', saved_selection.get('order', None)),
            'tagged': request.GET.get('tagged', saved_selection.get('tagged', None)),
        }
        
        queryset = Vote.objects.filter_and_order(**options)
        
        friend_page = {}
        friend_page['vote_type'] = urllib.quote(request.GET.get('vote_type',saved_selection.get('vote_type','all')).encode('utf8'))
        friend_page['tagged'] = urllib.quote(request.GET.get('tagged', saved_selection.get('tagged','all')).encode('utf8'))
        friend_page['time'] = urllib.quote(request.GET.get('time', saved_selection.get('time','all')).encode('utf8'))
        friend_page['order'] = urllib.quote(request.GET.get('order',saved_selection.get('order','time')).encode('utf8'))

        request.session[self.session_votes_key] = friend_page
        
        r = {}

        for key, value, name in self.friend_pages:
            page = friend_page.copy()
            current = False
            if page[key]==value:
                current = True
                if key=='vote_type':
                    self.extra_context['title'] = name
            else:
                page[key] = value
            url =  "./?%s" % urllib.urlencode(page)
            if key not in r:
                r[key] = []
            r[key].append((url, name, current))        

        #[(_('all'),'&'.join([time,order])), (_('law approval'))],[],[]]        
        self.extra_context['friend_pages'] = r
        watched_members = request.user.get_profile().followed_members.all()\
                if request.user.is_authenticated() else False

        self.extra_context['watched_members'] = watched_members
        return super(VoteListView, self).render_list(request, queryset=queryset, **kwargs)

    def render_object(self, request, object_id, extra_context=None, **kwargs):
        vote = get_object_or_404(Vote, pk=object_id)
        if not extra_context:
            extra_context = {}
        extra_context['title'] = vote.title

        related_bills = list(vote.bills_pre_votes.all())
        if Bill.objects.filter(approval_vote=vote).count()>0:
            related_bills.append(vote.bill_approved)
        if Bill.objects.filter(first_vote=vote).count()>0:
            related_bills.extend(vote.bills_first.all())
        extra_context['bills'] = related_bills
        return super(VoteListView, self).render_object(request, object_id,
                              extra_context=extra_context, **kwargs)       


@login_required
def submit_tags(request,object_id):
    if request.method == 'POST': # If the form has been submitted...
        form = TagForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            v = Vote.objects.get(pk=object_id)
            v.tags = u'%s,' % form.cleaned_data['tags'].replace('"',u'”') # add comma in the end to force treatment as comma-separated list
                                                                          # replace " with ” to support hebrew initials


    return HttpResponseRedirect("/vote/%s" % object_id)

@login_required
def suggest_tag(request,object_id):
    if request.method == 'POST' and 'tag_id' in request.POST: # If the form has been submitted...
        v = Vote.objects.get(pk=object_id)
        tag = Tag.objects.get(pk=request.POST['tag_id'])
        ctype = ContentType.objects.get_for_model(v)
        (ti, created) = TaggedItem._default_manager.get_or_create(tag=tag, content_type=ctype, object_id=object_id)
        (tv, created) = TagVote.objects.get_or_create(tagged_item=ti, user=request.user, defaults={'vote': 0})
        tv.vote = +1
        tv.save()
    return HttpResponse("OK")



@login_required
def vote_on_tag(request,object_id,tag_id,vote):
    v = Vote.objects.get(pk=object_id)
    ti = TaggedItem.objects.filter(tag__id=tag_id).filter(object_id=v.id)[0]
    (tv, created) = TagVote.objects.get_or_create(tagged_item=ti, user=request.user, defaults={'vote': 0})
    tv.vote = vote
    tv.save()
    return HttpResponseRedirect("/vote/%s" % object_id)

def tagged(request,tag):
    title = ugettext_lazy('Votes tagged %(tag)s') % {'tag': tag}
    try:
        return tagged_object_list(request, queryset_or_model = Vote, tag=tag, extra_context={'title':title})
    except Http404:
        return object_list(request, queryset=Vote.objects.none(), extra_context={'title':title})

