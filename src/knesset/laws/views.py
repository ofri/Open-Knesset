#encoding: utf-8
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.views.generic.list_detail import object_list, object_detail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.db.models import Count, Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse

from tagging.models import Tag, TaggedItem
from tagging.views import tagged_object_list
from tagging.utils import get_tag
import tagging
from actstream import action
from knesset.utils import limit_by_request
from knesset.laws.models import *
from knesset.mks.models import Member
from knesset.tagvotes.models import TagVote
from knesset.hashnav.views import ListDetailView
from knesset.hashnav import DetailView, ListView, method_decorator
from knesset.agendas.models import Agenda

import urllib
import urllib2
import difflib
import logging 
import datetime
logger = logging.getLogger("open-knesset.laws.views")

def bill_tags_cloud(request, min_posts_count=1):
    member = None
    if 'member' in request.GET: 
        member = get_object_or_404(Member, pk=request.GET['member'])
        tags_cloud = Tag.objects.usage_for_queryset(member.bills.all(),counts=True)
        tags_cloud = tagging.utils.calculate_cloud(tags_cloud)
        title = _('Bills by %(member)s by tag') % {'member':member.name}
    else:
        title = _('Bills by tag')
        tags_cloud = Tag.objects.cloud_for_model(Bill)
    return render_to_response("laws/bill_tags_cloud.html",
        {"tags_cloud": tags_cloud, "title":title, "member":member}, context_instance=RequestContext(request))

def bill_tag(request, tag):
    tag_instance = get_tag(tag)
    if tag_instance is None:
        raise Http404(_('No Tag found matching "%s".') % tag)        
    
    extra_context = {'tag':tag_instance}
    extra_context['tag_url'] = reverse('bill-tag',args=[tag_instance])
    if 'member' in request.GET:
        try:
            member_id = int(request.GET['member'])
        except ValueError:
            raise Http404(_('No Member found matching "%s".') % request.GET['member']) 
        extra_context['member'] = get_object_or_404(Member, pk=request.GET['member'])
        extra_context['member_url'] = reverse('member-detail',args=[extra_context['member'].id])
        extra_context['title'] = _('Bills tagged %(tag)s by %(member)s') % {'tag': tag, 'member':extra_context['member'].name}
        qs = extra_context['member'].bills.all()
    else: # only tag is given
        extra_context['title'] = _('Bills tagged %(tag)s') % {'tag': tag}
        qs = Bill

    queryset = TaggedItem.objects.get_by_model(qs, tag_instance)
    bill_proposers = [b.proposers.all() for b in TaggedItem.objects.get_by_model(Bill, tag_instance)]
    d = {}
    for bill in bill_proposers:
        for p in bill:
            d[p] = d.get(p,0)+1
    # now d is a dict: MK -> number of proposals in this tag
    mks = d.keys()
    for mk in mks:
        mk.count = d[mk]
    mks = tagging.utils.calculate_cloud(mks)
    extra_context['members'] = mks
    return object_list(request, queryset,
    #return tagged_object_list(request, queryset_or_model=qs, tag=tag, 
        template_name='laws/bill_list_by_tag.html', extra_context=extra_context)

def bill_auto_complete(request):
    if request.method != 'GET':
        raise Http404

    if not 'query' in request.GET:
        raise Http404

    options = Bill.objects.filter(title__icontains=request.GET['query'])[:30]
    data = []
    suggestions = []
    for i in options:
        data.append(i.id)
        suggestions.append(i.title)

    result = { 'query': request.GET['query'], 'suggestions':suggestions, 'data':data }

    return HttpResponse(simplejson.dumps(result), mimetype='application/json')

def vote_tags_cloud(request, min_posts_count=1):
    member = None
    if 'member' in request.GET: 
        member = get_object_or_404(Member, pk=request.GET['member'])
        tags_cloud = Tag.objects.usage_for_queryset(member.votes.all(),counts=True)
        tags_cloud = tagging.utils.calculate_cloud(tags_cloud)
        title = _('Votes by %(member)s by tag') % {'member':member.name}
    else:
        title = _('Votes by tag')
        tags_cloud = Tag.objects.cloud_for_model(Vote)
    return render_to_response("laws/vote_tags_cloud.html",
        {"tags_cloud": tags_cloud, "title":title, "member":member}, context_instance=RequestContext(request))

def vote_tag(request, tag):
    tag_instance = get_tag(tag)
    if tag_instance is None:
        raise Http404(_('No Tag found matching "%s".') % tag)        
    
    extra_context = {'tag':tag_instance}
    extra_context['tag_url'] = reverse('vote-tag',args=[tag_instance])
    if 'member' in request.GET: 
        extra_context['member'] = get_object_or_404(Member, pk=request.GET['member'])
        extra_context['member_url'] = reverse('member-detail',args=[extra_context['member'].id])
        extra_context['title'] = ugettext_lazy('Votes tagged %(tag)s by %(member)s') % {'tag': tag, 'member':extra_context['member'].name}
        qs = extra_context['member'].votes.all()
    else: # only tag is given
        extra_context['title'] = ugettext_lazy('Votes tagged %(tag)s') % {'tag': tag}
        qs = Vote

    queryset = TaggedItem.objects.get_by_model(qs, tag_instance)
    vote_attendence = [v.votes.all() for v in TaggedItem.objects.get_by_model(Vote, tag_instance)]
    d = {}
    for vote in vote_attendence:
        for v in vote:
            d[v] = d.get(v,0)+1
    # now d is a dict: MK -> number of votes in this tag
    mks = d.keys()    
    for mk in mks:
        mk.count = d[mk]
    average = float(sum([mk.count for mk in mks]))/len(mks)
    mks = [mk for mk in mks if mk.count>=average]
    mks = tagging.utils.calculate_cloud(mks)
    extra_context['members'] = mks
    return object_list(request, queryset,
    #return tagged_object_list(request, queryset_or_model=qs, tag=tag, 
        template_name='laws/vote_list_by_tag.html', extra_context=extra_context)



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

        action.send(self.request.user, verb='added-vote-to-bill',
                description=vote,
                target=bill,
                timestamp=datetime.datetime.now())
        return HttpResponseRedirect(".")

_('added-vote-to-bill')

class BillListView (ListView):
    friend_pages = [
            ('stage','all',_('All stages')),
    ]
    friend_pages.extend([('stage',x[0],_(x[1])) for x in BILL_STAGE_CHOICES])

    bill_stages = { 'proposed':Q(stage__isnull=False),
                    'pre':Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6'),
                    'first':Q(stage='4')|Q(stage='5')|Q(stage='6'),
                    'approved':Q(stage='6'),
                  }
    bill_stages_names = { 'proposed':'Bills proposed',
                    'pre':'Bills passed pre-vote',
                    'first':'Bills passed first vote',
                    'approved':'Bills approved',
                  }

    def get_queryset(self):
        stage = self.request.GET.get('stage', False)
        booklet = self.request.GET.get('booklet', False)
        member = self.request.GET.get('member', False)
        if member:
            member = get_object_or_404(Member, pk=member)
            qs = member.bills.all()			
        else:
            qs = self.queryset._clone()
        if stage and stage!='all':
            if stage in self.bill_stages:
                qs = qs.filter(self.bill_stages[stage])
            else:
                qs = qs.filter(stage=stage)            
        elif booklet:
            kps = KnessetProposal.objects.filter(booklet_number=booklet).values_list('id',flat=True)
            qs = qs.filter(knesset_proposal__in=kps)        
        return qs

    def get_context(self):
        context = super(BillListView, self).get_context()       
        r = [['?%s=%s'% (x[0],x[1]),x[2],False,x[1]] for x in self.friend_pages]
        stage = self.request.GET.get('stage', False)
        booklet = self.request.GET.get('booklet', False)
        member = self.request.GET.get('member', False)
        if stage and stage!='all':
            for x in r:
                if x[3]==stage:
                    x[2] = True
                    break
            if stage in self.bill_stages_names:
                context['stage'] = self.bill_stages_names.get(stage)
                context['title'] = _('%(stage)s') % {'stage': self.bill_stages_names[stage]}
        elif booklet:
            context['title']=_('Bills published in knesset booklet number %s') % booklet
        else:
            r[0][2] = True                
        if member:
            context['member'] = get_object_or_404(Member, pk=member)
            context['member_url'] = reverse('member-detail',args=[context['member'].id])            
            if stage in self.bill_stages_names:
                context['title'] = _('%(stage)s by %(member)s') % {'stage': self.bill_stages_names[stage], 'member':context['member'].name}
            else:
                context['title'] = _('Bills by %(member)s') % {'member':context['member'].name}
            
        context['friend_pages'] = r
        return context
        
class VoteListView(ListView):

    session_votes_key = 'selected_votes'
    
    friend_pages = [
            ('type','all',_('All votes')),
            ('type','law-approve', _('Law Approvals')),
            ('type','second-call', _('Second Call')),
            ('type','demurrer', _('Demurrer')),
            ('type','no-confidence', _('Motion of no confidence')),
            ('type','pass-to-committee', _('Pass to committee')),
            ('type','continuation', _('Continuation')),
            ('tagged','all',_('All')),
            ('tagged','false',_('Untagged Votes')),
            ('tagged','true',_('Tagged Votes')),            
            ('since','7',_('Last Week')),
            ('since','30',_('Last Month')),
            ('since','all',_('All times')),
            ('order','time',_('Time')),
            ('order','controversy', _('Controversy')),
            ('order','against-party',_('Against Party')),
            ('order','votes',_('Number of votes')),
            
        ]

    def get_queryset(self, **kwargs):
        saved_selection = self.request.session.get(self.session_votes_key, dict())
        self.options = {}
        for key in ['type', 'tagged', 'since', 'order']:
            self.options[key] = self.request.GET.get(key, 
                                         saved_selection.get(key, None))
        
        return Vote.objects.filter_and_order(**self.options)
        
    def get_context(self):
        context = super(VoteListView, self).get_context()       
        friend_page = {}
        for key in ['type', 'tagged', 'since', 'order']:
            if self.options[key]:
                friend_page[key] = urllib.quote(self.options[key].encode('utf8'))
            else:
                friend_page[key] = 'all' if key!='order' else 'time'
        self.request.session[self.session_votes_key] = friend_page
        
        r = {}

        for key, value, name in self.friend_pages:
            page = friend_page.copy()
            current = False
            if page[key]==value:
                current = True
                if key=='type':
                    context['title'] = name
            else:
                page[key] = value
            url =  "./?%s" % urllib.urlencode(page)
            if key not in r:
                r[key] = []
            r[key].append((url, name, current))        

        context['friend_pages'] = r
        if self.request.user.is_authenticated():
            context['watched_members'] = \
                self.request.user.get_profile().members
        else:
            context['watched_members'] = False

        return context

class VoteDetailView(DetailView):
    def get_context(self):
        context = super(VoteDetailView, self).get_context()       
        vote = context['object']
        context['title'] = vote.title

        related_bills = list(vote.bills_pre_votes.all())
        if Bill.objects.filter(approval_vote=vote).count()>0:
            related_bills.append(vote.bill_approved)
        if Bill.objects.filter(first_vote=vote).count()>0:
            related_bills.extend(vote.bills_first.all())
        context['bills'] = related_bills
        
        if self.request.user.is_authenticated():
            context['agendavotes'] = vote.agendavote_set.filter(agenda__in=Agenda.objects.get_relevant_for_user(user=self.request.user))
        else:
            context['agendavotes'] = vote.agendavote_set.filter(agenda__in=Agenda.objects.get_relevant_for_user(user=None))
        
        return context


@login_required
def suggest_tag(request, object_type, object_id):
    """add a POSTed tag_id to object_type object_id, and also vote this tagging up by the current user"""
    ctype = get_object_or_404(ContentType,model=object_type)
    model_class = ctype.model_class()
    
    if request.method == 'POST' and 'tag_id' in request.POST: # If the form has been submitted...
        #o = model_class.objects.get(pk=object_id)
        tag = get_object_or_404(Tag,pk=request.POST['tag_id'])        
        (ti, created) = TaggedItem._default_manager.get_or_create(tag=tag, content_type=ctype, object_id=object_id)
        (tv, created) = TagVote.objects.get_or_create(tagged_item=ti, user=request.user, defaults={'vote': 0})
        tv.vote = +1
        tv.save()
        
        action.send(request.user,verb='tag-voted', target=ti, description='Vote Up')
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
                
        vote = int(vote) # vote is u'-1',u'0',u'+1' (not a Vote model)                
        if vote > 0: 
            tv.vote = 1
            action.send(request.user,verb='tag-voted', target=ti, description='Vote Up')
        elif vote < 0:
            tv.vote = -1
            action.send(request.user,verb='voted down on a tag', target=ti, description='Vote Down')
        else:       
            tv.vote = 0
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

def vote_auto_complete(request):
    if request.method != 'GET':
        raise Http404

    if not 'query' in request.GET:
        raise Http404

    options = Vote.objects.filter(title__icontains=request.GET['query'])[:30]

    data = []
    suggestions = []
    for i in options:
        data.append(i.id)
        suggestions.append(i.title)

    result = { 'query': request.GET['query'], 'suggestions':suggestions, 'data':data }

    return HttpResponse(simplejson.dumps(result), mimetype='application/json')

