from datetime import date
from django.conf import settings
from django.template import Context
from django.views.generic.list_detail import object_list, object_detail
from django.db.models import Count, Sum, Q
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from tagging.models import Tag
import tagging
from knesset.utils import limit_by_request
from knesset.mks.models import Member, Party
from knesset.mks.forms import VerbsForm
from knesset.laws.models import MemberVotingStatistics
from knesset.hashnav import ListView, DetailView, method_decorator

from actstream import actor_stream
from django.contrib.auth.decorators import login_required
import logging
import sys,traceback
logger = logging.getLogger("open-knesset.mks")

class MemberListView(ListView):

    def render_html(self, *args, **kwargs):
        ''' cache the html returned by render_html '''
        info = self.request.GET.get('info','bills_pre')
        response = cache.get('mks_list_by_%s' % info)
        if response:
            return response
        response = super(MemberListView, self).render_html(*args, **kwargs)
        cache.set('mks_list_by_%s' % info, response, 30*60)
        return response

    def get_template_names(self):
        info = self.request.GET.get('info','bills_pre')
        if info=='abc':
            return ['mks/member_list.html']
        elif info=='graph':
            return ['mks/member_graph.html']
        else:
            return ['mks/member_list_with_bars.html']

    def get_context(self):
        context = super(MemberListView, self).get_context()
        info = self.request.GET.get('info','bills_pre')
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
        return context

class MemberDetailView(DetailView):

    # TODO: there should be a simpler way, no?
    @method_decorator(cache_page(30*60))
    def GET(self, *args, **kwargs):
        return super(MemberDetailView, self).GET(*args, **kwargs)

    def get_context (self):
        context = super(MemberDetailView, self).get_context()
        member = context['object']
        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = member in p.followed_members.all()
        else:
            watched = False
            
        verbs = None
        if 'verbs' in self.request.GET:
            verbs_form = VerbsForm(request.GET)
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
        context.update({'watched_member': watched,
                'actions': actor_stream(member).filter(verb__in=verbs),
                'verbs_form': verbs_form,
                'bills_statistics':bills_statistics,
                'bills_tags':bills_tags,
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
                
        return context
