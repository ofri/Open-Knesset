from operator import itemgetter, attrgetter
from datetime import date
from django.conf import settings
from django.template import Context
from django.views.generic.list_detail import object_list, object_detail
from django.db.models import Count, Sum, Q
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
import json
from django.core.cache import cache
from tagging.models import Tag
import tagging
from knesset.utils import limit_by_request
from knesset.mks.models import Member, Party, find_possible_members, find_possible_parties
from knesset.mks.forms import VerbsForm
from knesset.laws.models import MemberVotingStatistics, Bill
from knesset.hashnav import ListView, DetailView, method_decorator
from knesset.agendas.models import Agenda

from actstream import actor_stream
from django.contrib.auth.decorators import login_required
import logging
import sys,traceback
logger = logging.getLogger("open-knesset.mks")

class MemberListView(ListView):

    def get_template_names(self):
        info = self.request.GET.get('info','bills_pre')
        if info=='abc':
            return ['mks/member_list.html']
        elif info=='graph':
            return ['mks/member_graph.html']
        else:
            return ['mks/member_list_with_bars.html']

    def get_context(self):
        info = self.request.GET.get('info','bills_pre')
        context = cache.get('member_list_by_%s' % info)
        if context:
            return context
        context = super(MemberListView, self).get_context()
        qs = context['object_list']
        context['friend_pages'] = [['.?info=abc',_('By ABC'), False],
                              ['.?info=bills_proposed',_('By number of bills proposed'), False],
                              ['.?info=bills_pre',_('By number of bills pre-approved'), False],
                              ['.?info=bills_first',_('By number of bills first-approved'), False],
                              ['.?info=bills_approved',_('By number of bills approved'), False],
                              ['.?info=votes', _('By number of votes per month'), False],
                              ['.?info=presence', _('By average weekly hours of presence'), False],
                              ['.?info=committees', _('By average monthly committee meetings'), False],
                              ['.?info=graph', _('Graphical view'), False]]
        if info=='abc':
            context['friend_pages'][0][2] = True
            context['title'] = _('Members')
        elif info=='bills_proposed':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.count()
            qs.sort(key=lambda x:x.extra, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.bills.count()
            context['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            context['friend_pages'][1][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By number of bills proposed'))
        elif info=='bills_pre':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.filter(Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
            qs.sort(key=lambda x:x.extra, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.bills.filter(Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
            context['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            context['friend_pages'][2][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By number of bills pre-approved'))
        elif info=='bills_first':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.filter(Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
            qs.sort(key=lambda x:x.extra, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.bills.filter(Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
            context['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            context['friend_pages'][3][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By number of bills first-approved'))
        elif info=='bills_approved':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.filter(stage='6').count()
            qs.sort(key=lambda x:x.extra, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.bills.filter(stage='6').count()
            context['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            context['friend_pages'][4][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By number of bills approved'))
        elif info=='votes':
            qs = list(qs)
            vs = list(MemberVotingStatistics.objects.all())
            vs = dict(zip([x.member_id for x in vs],vs))
            for x in qs:
                x.extra = vs[x.id].average_votes_per_month()
            qs.sort(key=lambda x:x.extra, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.voting_statistics.average_votes_per_month()
            context['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            context['friend_pages'][5][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By number of votes per month'))
        elif info=='presence':
            qs = list(qs)
            for x in qs:
                x.extra = x.average_weekly_presence()
            qs.sort(key=lambda x:x.extra or 0, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.average_weekly_presence()
            context['past_mks'].sort(key=lambda x:x.extra or 0, reverse=True)
            context['friend_pages'][6][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By average weekly hours of presence'))
        elif info=='committees':
            qs = list(qs)
            for x in qs:
                x.extra = x.committee_meetings_per_month()
            qs.sort(key=lambda x:x.extra or 0, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.committee_meetings_per_month()
            context['past_mks'].sort(key=lambda x:x.extra or 0, reverse=True)
            context['friend_pages'][7][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0            
            context['title'] = "%s %s" % (_('Members'), _('By average monthly committee meetings'))
        elif info=='graph':
            context['friend_pages'][8][2] = True
            context['title'] = "%s %s" % (_('Members'), _('Graphical view'))
        context['object_list']=qs
        cache.set('member_list_by_%s' % info, context, 900)
        return context

class MemberDetailView(DetailView):

    def get_context (self):
        context = super(MemberDetailView, self).get_context()
        member = context['object']
        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = member in p.members
        else:
            watched = False
            
        verbs = None
        if 'verbs' in self.request.GET:
            verbs_form = VerbsForm(self.request.GET)
            if verbs_form.is_valid():
                verbs = verbs_form.cleaned_data['verbs']
        if verbs==None:
            verbs = ('proposed', 'posted')
            verbs_form = VerbsForm({'verbs': verbs})

        bills_statistics = {}
        bills_statistics['proposed'] = member.bills.count()
        bills_statistics['pre'] = member.bills.filter(Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
        bills_statistics['first'] = member.bills.filter(Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
        bills_statistics['approved'] = member.bills.filter(stage='6').count()

        bills_tags = Tag.objects.usage_for_queryset(member.bills.all(),counts=True)
        #bills_tags.sort(key=lambda x:x.count,reverse=True)
        bills_tags = tagging.utils.calculate_cloud(bills_tags)

        agendas = Agenda.objects.get_selected_for_instance(member, top=3, bottom=3)
        agendas = agendas['top'] + agendas['bottom']
        for agenda in agendas:
            agenda.watched=False
        if self.request.user.is_authenticated():
            watched_agendas = self.request.user.get_profile().agendas
            for watched_agenda in watched_agendas:
                if watched_agenda in agendas:
                    agendas[agendas.index(watched_agenda)].watched = True
                else:
                    watched_agenda.score = watched_agenda.member_score(member)
                    watched_agenda.watched = True
                    agendas.append(wathced_agenda)
        agendas.sort(key=attrgetter('score'), reverse=True)
        
        context.update({'watched_member': watched,
                'actions': actor_stream(member).filter(verb__in=verbs),
                'verbs_form': verbs_form,
                'bills_statistics':bills_statistics,
                'bills_tags':bills_tags,
                'agendas':agendas
               })
        return context

class PartyListView(ListView):
    def get_context(self):
        context = super(PartyListView, self).get_context()
        qs = context['object_list']
        info = self.request.GET.get('info','seats')
        context['coalition'] = qs.filter(is_coalition=True)
        context['opposition'] = qs.filter(is_coalition=False)
        context['friend_pages'] = [['.',_('By Number of seats'), False],
                              ['.?info=votes-per-seat', _('By votes per seat'), False],
                              ['.?info=discipline', _('By factional discipline'), False],
                              ['.?info=coalition-discipline', _('By coalition/opposition discipline'), False],
                              ['.?info=residence-centrality', _('By residence centrality'), False],
                              ['.?info=residence-economy', _('By residence economy'), False],
                              ['.?info=bills-proposed', _('By bills proposed'), False],
                              ['.?info=bills-pre', _('By bills passed pre vote'), False],
                              ['.?info=bills-first', _('By bills passed first vote'), False],
                              ['.?info=bills-approved', _('By bills approved'), False],
                              ]

        if info:
            if info=='seats':
                context['coalition']  =  context['coalition'].annotate(extra=Sum('number_of_seats')).order_by('-extra')
                context['opposition'] = context['opposition'].annotate(extra=Sum('number_of_seats')).order_by('-extra')
                context['friend_pages'][0][2] = True
                context['norm_factor'] = 1
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties'))
            if info=='votes-per-seat':
                m = 0
                for p in context['coalition']:
                    p.extra = p.voting_statistics.votes_per_seat()
                    if p.extra > m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = p.voting_statistics.votes_per_seat()
                    if p.extra > m:
                        m = p.extra
                context['friend_pages'][1][2] = True
                context['norm_factor'] = m/20
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties'))

            if info=='discipline':
                m = 100
                for p in context['coalition']:
                    p.extra = p.voting_statistics.discipline()
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = p.voting_statistics.discipline()
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][2][2] = True
                context['norm_factor'] = (100.0-m)/15
                context['baseline'] = m - 2
                context['title'] = "%s" % (_('Parties'))

            if info=='coalition-discipline':
                m = 100
                for p in context['coalition']:
                    p.extra = p.voting_statistics.coalition_discipline()
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = p.voting_statistics.coalition_discipline()
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][3][2] = True
                context['norm_factor'] = (100.0-m)/15
                context['baseline'] = m - 2
                context['title'] = "%s" % (_('Parties'))
                
            if info=='residence-centrality':
                m = 10
                for p in context['coalition']:
                    rc = [member.residence_centrality for member in p.members.all() if member.residence_centrality]
                    p.extra = round(float(sum(rc))/len(rc),1)
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    rc = [member.residence_centrality for member in p.members.all() if member.residence_centrality]
                    p.extra = round(float(sum(rc))/len(rc),1)
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][4][2] = True
                context['norm_factor'] = (10.0-m)/15
                context['baseline'] = m-1
                context['title'] = "%s" % (_('Parties by residence centrality'))

            if info=='residence-economy':
                m = 10
                for p in context['coalition']:
                    rc = [member.residence_economy for member in p.members.all() if member.residence_economy]
                    p.extra = round(float(sum(rc))/len(rc),1)
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    rc = [member.residence_economy for member in p.members.all() if member.residence_economy]
                    p.extra = round(float(sum(rc))/len(rc),1)
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][5][2] = True
                context['norm_factor'] = (10.0-m)/15
                context['baseline'] = m-1
                context['title'] = "%s" % (_('Parties by residence economy'))

            if info=='bills-proposed':
                m = 9999
                for p in context['coalition']:
                    p.extra = len(set(Bill.objects.filter(proposers__current_party=p).values_list('id',flat=True)))/p.number_of_seats
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = len(set(Bill.objects.filter(proposers__current_party=p).values_list('id',flat=True)))/p.number_of_seats
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][6][2] = True
                context['norm_factor'] = m/2
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties by number of bills proposed per seat'))

            if info=='bills-pre':
                m = 9999
                for p in context['coalition']:
                    p.extra = round(float(len(set(Bill.objects.filter(Q(proposers__current_party=p),Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = round(float(len(set(Bill.objects.filter(Q(proposers__current_party=p),Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][7][2] = True
                context['norm_factor'] = m/2
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties by number of bills passed pre vote per seat'))

            if info=='bills-first':
                m = 9999
                for p in context['coalition']:
                    p.extra = round(float(len(set(Bill.objects.filter(Q(proposers__current_party=p),Q(stage='4')|Q(stage='5')|Q(stage='6')).values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = round(float(len(set(Bill.objects.filter(Q(proposers__current_party=p),Q(stage='4')|Q(stage='5')|Q(stage='6')).values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][8][2] = True
                context['norm_factor'] = m/2
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties by number of bills passed first vote per seat'))

            if info=='bills-approved':
                m = 9999
                for p in context['coalition']:
                    p.extra = round(float(len(set(Bill.objects.filter(proposers__current_party=p,stage='6').values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = round(float(len(set(Bill.objects.filter(proposers__current_party=p,stage='6').values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][9][2] = True
                context['norm_factor'] = m/2
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties by number of bills passed approved per seat'))                    
        return context

class PartyDetailView(DetailView):
    def get_context (self):
        context = super(PartyDetailView, self).get_context()
        party = context['object']
        agendas = []
        for agenda in Agenda.objects.all():
            agendas.append( {'name':agenda.name,'id':agenda.id,'score':agenda.party_score(party)} )
            if agendas[-1]['score'] < 0:
                agendas[-1]['class'] = 'against'
            else: 
                agendas[-1]['class'] = 'for' 
        agendas.sort(key=itemgetter('score'), reverse=True)
        context.update({'agendas':agendas})
        return context


def member_auto_complete(request):
    if request.method != 'GET':
        raise Http404

    if not 'query' in request.GET:
        raise Http404

    suggestions = map(lambda member: member.name, Member.objects.filter(name__icontains=request.GET['query'])[:30])

    result = { 'query': request.GET['query'], 'suggestions':suggestions }

    return HttpResponse(json.dumps(result), mimetype='application/json')


object_finders = {'member':find_possible_members, 'party':find_possible_parties}        
def object_by_name(request, object_type):
    name = request.GET.get('q','')
    name = name.replace('%20',' ')    
    results = object_finders[object_type](name)
    if (request.is_ajax())or(request.GET.has_key('xhr')):
        try:
            for r in results:
                r['url'] = reverse('%s-detail' % object_type,args=[r['id']])
            return HttpResponse(json.dumps({'possible':results},ensure_ascii=False))
        except Exception,e:
            print e
    if results:
        return HttpResponseRedirect(reverse('%s-detail' % object_type,args=[results[0]['id']]))
    raise Http404(_('No %(object_type)s found matching "%(name)s".', {'object_type':object_type,'name':name}))

def party_by_name(request):
    return object_by_name(request, 'party')
    
def member_by_name(request):
    return object_by_name(request, 'member')

