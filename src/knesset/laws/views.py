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
from knesset.hashnav import DetailView, ListView, method_decorator

import urllib
import urllib2
import difflib
import logging 
import datetime
logger = logging.getLogger("open-knesset.laws.views")

class BillDetailView (DetailView):
    allowed_methods = ['GET', 'POST']
    def get_context(self, *args, **kwargs):
        context = super(BillDetailView, self).get_context(*args, **kwargs)       
        bill = context['object']
        try:
            context['title'] = "%s %s" % (bill.law.title, bill.title)
        except AttributeError:
            context['title'] = bill.title

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
            context['close_votes'] = close_votes
        except Exception, e:
            pass
        return context

    @method_decorator(login_required)
    def POST(self, object_id, **kwargs):
        vote = None
        bill = get_object_or_404(Bill, pk=object_id)
        user_input_type = self.request.POST.get('user_input_type')
        if user_input_type == 'approval vote':
            vote = Vote.objects.get(pk=self.request.POST.get('vote_id'))
            bill.approval_vote = vote
            bill.update_stage()
        if user_input_type == 'first vote':
            vote = Vote.objects.get(pk=self.request.POST.get('vote_id'))
            bill.first_vote = vote
            bill.update_stage()
        if user_input_type == 'pre vote':
            vote = Vote.objects.get(pk=self.request.POST.get('vote_id'))
            bill.pre_votes.add(vote)
            bill.update_stage()

        action.send(self.request.user, verb='merged',
                description=vote,
                target=bill,
                timestamp=datetime.datetime.now())
        return HttpResponseRedirect(".")

class BillListView (ListView):
    friend_pages = [
            ('stage','all',_('All stages')),
    ]
    friend_pages.extend([('stage',x[0],_(x[1])) for x in BILL_STAGE_CHOICES])

    def get_queryset(self):
        stage = self.request.GET.get('stage', False)
        booklet = self.request.GET.get('booklet', False)
        if stage and stage!='all':
            return self.queryset._clone().filter(stage=stage)
        elif booklet:
            kps = KnessetProposal.objects.filter(booklet_number=booklet).values_list('id',flat=True)
            return self.queryset._clone().filter(knesset_proposal__in=kps)
        else:
            return self.queryset._clone()

    def get_context(self):
        context = super(BillListView, self).get_context()       
        r = [['?%s=%s'% (x[0],x[1]),x[2],False,x[1]] for x in self.friend_pages]
        stage = self.request.GET.get('stage', False)
        booklet = self.request.GET.get('booklet', False)
        if stage and stage!='all':
            for x in r:
                if x[3]==stage:
                    x[2] = True
                    break
        elif booklet:
            context['title']=_('Bills published in knesset booklet number %s') % booklet 
        else:
            r[0][2] = True
        context['friend_pages'] = r
        return context
        
class LawView (DetailView):

    def get_context(self, *args, **kwargs):
        law = Law.objects.get(pk=object_id)
        pps = PrivateProposal.objects.filter(law=law).annotate(c=Count('knesset_proposals')).filter(c=0).order_by('title')
        kps = KnessetProposal.objects.filter(law=law)
        context['pps'] = pps
        extra_context['kps'] = kps
        extra_context['title'] = law.title
        

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
def suggest_tag(request, object_type, object_id):
    """add a POSTed tag_id to object_type object_id, and also vote this tagging up by the current user"""
    try:
        ctype = ContentType.objects.get(model=object_type)
        model_class = ctype.model_class()
    except:
        return HttpResponse("Object type not found!")
    if request.method == 'POST' and 'tag_id' in request.POST: # If the form has been submitted...
        #o = model_class.objects.get(pk=object_id)
        tag = Tag.objects.get(pk=request.POST['tag_id'])        
        (ti, created) = TaggedItem._default_manager.get_or_create(tag=tag, content_type=ctype, object_id=object_id)
        (tv, created) = TagVote.objects.get_or_create(tagged_item=ti, user=request.user, defaults={'vote': 0})
        tv.vote = +1
        tv.save()
    return HttpResponse("OK")

@login_required
def vote_on_tag(request, object_type, object_id, tag_id, vote):
    """request.user is voting vote (-1/0/+1) for tag on object_type with object_id
       Can be used to vote on a tagged vote, or a tagged bill"""       
    try:
        ctype = ContentType.objects.get(model=object_type)
        model_class = ctype.model_class()        
        o = model_class.objects.get(pk=object_id)
        ti = TaggedItem.objects.filter(tag__id=tag_id).filter(object_id=o.id)[0]
        (tv, created) = TagVote.objects.get_or_create(tagged_item=ti, user=request.user, defaults={'vote': 0})
        tv.vote = vote # this is -1,0,+1 (not a Vote model)
        tv.save()
    except:
        pass
    return HttpResponseRedirect("/%s/%s" % (object_type,object_id))

def tagged(request,tag):
    title = ugettext_lazy('Votes tagged %(tag)s') % {'tag': tag}
    try:
        return tagged_object_list(request, queryset_or_model = Vote, tag=tag, extra_context={'title':title})
    except Http404:
        return object_list(request, queryset=Vote.objects.none(), extra_context={'title':title})

