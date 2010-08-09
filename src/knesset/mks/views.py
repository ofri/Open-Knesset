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

from knesset.utils import limit_by_request
from knesset.mks.models import Member, Party
from knesset.mks.forms import VerbsForm
from knesset.laws.models import MemberVotingStatistics
from knesset.hashnav.views import ListDetailView

from django.contrib.auth.decorators import login_required
import logging
import sys,traceback
logger = logging.getLogger("open-knesset.mks")

member_context = dict (quesryset =
                       Member.objects.all(),
                      paginate_by = 20)

def member (request, pk=None):
    qs = Member.objects.all()
    if pk:
        return object_detail(request, queryset=qs, object_id=pk,
                             template_name='mks/member.html')
    else:
        return object_list(request, queryset=member_context['queryset'],
                           template_name='mks/members.html')

def party (request, pk=None):
    qs = Party.objects.all()
    if pk:
        return object_detail(request, queryset=qs, object_id=pk,
                             template_name='mks/party.html')
    else:
        # return a list
        qs = limit_by_request(qs, request)
        return object_list(request, queryset=qs,template_name='mks/parties.html')

class MemberSelectView(ListDetailView):
    def render_list(self,request, **kwargs):
        ec = dict(self.extra_context) or {}
        if 'extra_context' in kwargs:
            ec.update(kwargs['extra_context'])
        selected_mks = request.session.get('selected_mks',dict())
        qs = self.queryset.all()
        for o in qs:
            if o.id in selected_mks:
                o.selected = True
        next = request.GET.get('next',None)
        if next:
            path = request.get_full_path()
            ec['next'] = path[path.find('=')+1:]

        return ListDetailView.render_list(self, request, queryset = qs, extra_context = ec, **kwargs)

    def handle_post(self, request, **kwargs):
        ''' post to toggle a followed object '''
        try:
            o_id = int(request.POST.get('object_id', None))
            o_type = request.POST.get('object_type', 'mks')
            key = 'selected_%s' % o_type
            selected_mks = request.session.get(key ,dict())
            if o_id in selected_mks:
                del selected_mks[o_id]
            else:
                selected_mks[o_id] = True
            request.session[key] = selected_mks
        except Exception, e:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            logger.error("%s", ''.join(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)))
        # post should return json
        return self.render_list(request, **kwargs)


class MemberListView(ListDetailView):
    def render_list(self,request, **kwargs):
        info = request.GET.get('info','bills_pre')
        response = cache.get('mks_list_by_%s' % info)
        if response:
            return response
        qs = self.queryset.all()
        ec = dict(self.extra_context) or {}
        if 'extra_context' in kwargs:
            ec.update(kwargs['extra_context'])
        ec['friend_pages'] = [['.?info=abc',_('By ABC'), False],
                              ['.?info=bills_proposed',_('By number of bills proposed'), False],
                              ['.?info=bills_pre',_('By number of bills pre-approved'), False],
                              ['.?info=bills_first',_('By number of bills first-approved'), False],
                              ['.?info=bills_approved',_('By number of bills approved'), False],
                              ['.?info=votes', _('By number of votes per month'), False],
                              ['.?info=presence', _('By average weekly hours of presence'), False],
                              ['.?info=committees', _('By average monthly committee meetings'), False],
                              ['.?info=graph', _('Graphical view'), False]]
        template_name='mks/member_list_with_bars.html'
        if info=='abc':
            ec['friend_pages'][0][2] = True
            ec['title'] = _('Members')
            template_name='mks/member_list.html'
        elif info=='bills_proposed':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.count()
            qs.sort(key=lambda x:x.extra, reverse=True)
            ec['past_mks'] = list(ec['past_mks'])
            for x in ec['past_mks']:
                x.extra = x.bills.count()
            ec['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            ec['friend_pages'][1][2] = True
            ec['norm_factor'] = float(qs[0].extra)/50.0
            ec['title'] = "%s %s" % (_('Members'), _('By number of bills proposed'))
        elif info=='bills_pre':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.filter(Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
            qs.sort(key=lambda x:x.extra, reverse=True)
            ec['past_mks'] = list(ec['past_mks'])
            for x in ec['past_mks']:
                x.extra = x.bills.filter(Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
            ec['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            ec['friend_pages'][2][2] = True
            ec['norm_factor'] = float(qs[0].extra)/50.0
            ec['title'] = "%s %s" % (_('Members'), _('By number of bills pre-approved'))
        elif info=='bills_first':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.filter(Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
            qs.sort(key=lambda x:x.extra, reverse=True)
            ec['past_mks'] = list(ec['past_mks'])
            for x in ec['past_mks']:
                x.extra = x.bills.filter(Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
            ec['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            ec['friend_pages'][3][2] = True
            ec['norm_factor'] = float(qs[0].extra)/50.0
            ec['title'] = "%s %s" % (_('Members'), _('By number of bills first-approved'))
        elif info=='bills_approved':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.filter(stage='6').count()
            qs.sort(key=lambda x:x.extra, reverse=True)
            ec['past_mks'] = list(ec['past_mks'])
            for x in ec['past_mks']:
                x.extra = x.bills.filter(stage='6').count()
            ec['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            ec['friend_pages'][4][2] = True
            ec['norm_factor'] = float(qs[0].extra)/50.0
            ec['title'] = "%s %s" % (_('Members'), _('By number of bills approved'))
        elif info=='votes':
            qs = list(qs)
            vs = list(MemberVotingStatistics.objects.all())
            vs = dict(zip([x.member_id for x in vs],vs))
            for x in qs:
                x.extra = vs[x.id].average_votes_per_month()
            qs.sort(key=lambda x:x.extra, reverse=True)
            ec['past_mks'] = list(ec['past_mks'])
            for x in ec['past_mks']:
                x.extra = x.voting_statistics.average_votes_per_month()
            ec['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            ec['friend_pages'][5][2] = True
            ec['norm_factor'] = float(qs[0].extra)/50.0
            ec['title'] = "%s %s" % (_('Members'), _('By number of votes per month'))
        elif info=='presence':
            qs = list(qs)
            for x in qs:
                x.extra = x.average_weekly_presence()
            qs.sort(key=lambda x:x.extra or 0, reverse=True)
            ec['past_mks'] = list(ec['past_mks'])
            for x in ec['past_mks']:
                x.extra = x.average_weekly_presence()
            ec['past_mks'].sort(key=lambda x:x.extra or 0, reverse=True)
            ec['friend_pages'][6][2] = True
            ec['norm_factor'] = float(qs[0].extra)/50.0
            ec['title'] = "%s %s" % (_('Members'), _('By average weekly hours of presence'))
        elif info=='committees':
            qs = list(qs)
            for x in qs:
                x.extra = x.committee_meetings_per_month()
            qs.sort(key=lambda x:x.extra or 0, reverse=True)
            ec['past_mks'] = list(ec['past_mks'])
            for x in ec['past_mks']:
                x.extra = x.committee_meetings_per_month()
            ec['past_mks'].sort(key=lambda x:x.extra or 0, reverse=True)
            ec['friend_pages'][7][2] = True
            ec['norm_factor'] = float(qs[0].extra)/50.0            
            ec['title'] = "%s %s" % (_('Members'), _('By average monthly committee meetings'))
        elif info=='graph':
            ec['friend_pages'][8][2] = True
            ec['title'] = "%s %s" % (_('Members'), _('Graphical view'))
            template_name='mks/member_graph.html'

        response = ListDetailView.render_list(self,request, queryset=qs,
                                  template_name=template_name, extra_context=ec, **kwargs)
        cache.set('mks_list_by_%s' % info, response, 30*60)
        return response

    def get_object_context (self, request, object_id):
        from actstream import actor_stream
        member = get_object_or_404(Member,pk=object_id)
        if request.user.is_authenticated():
            p = request.user.get_profile()
            watched = member in p.followed_members.all()
        else:
            watched = False
            
        verbs = None
        if 'verbs' in request.GET:
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

        return {'watched_member': watched,
                'actions': actor_stream(member).filter(verb__in=verbs),
                'verbs_form': verbs_form,
                'bills_statistics':bills_statistics,
               }

    @method_decorator(cache_page(30*60))
    def render_object(self, request, object_id, extra_context={}, **kwargs):
        context = self.get_object_context(request, object_id)
        extra_context.update(context)
        return super(MemberListView, self).render_object(request, object_id,
                              extra_context=extra_context, **kwargs)



class PartyListView(ListDetailView):
    def render_list(self,request, **kwargs):
        qs = self.queryset.all()
        info = request.GET.get('info','seats')
        ec = {}
        if self.extra_context:
            ec.update(self.extra_context)
        if 'extra_context' in kwargs:
            ec.update(kwargs['extra_context'])
        ec['coalition'] = qs.filter(is_coalition=True)
        ec['opposition'] = qs.filter(is_coalition=False)
        ec['friend_pages'] = [['.',_('By Number of seats'), False],
                              ['.?info=votes-per-seat', _('By votes per seat'), False],
                              ['.?info=discipline', _('By factional discipline'), False],
                              ['.?info=coalition-discipline', _('By coalition/opposition discipline'), False],
                              ]

        if info:
            if info=='seats':
                ec['coalition']  =  ec['coalition'].annotate(extra=Sum('number_of_seats')).order_by('-extra')
                ec['opposition'] = ec['opposition'].annotate(extra=Sum('number_of_seats')).order_by('-extra')
                ec['friend_pages'][0][2] = True
                ec['norm_factor'] = 1
                ec['baseline'] = 0
                ec['title'] = "%s" % (_('Parties'))
            if info=='votes-per-seat':
                m = 0
                for p in ec['coalition']:
                    p.extra = p.voting_statistics.votes_per_seat()
                    if p.extra > m:
                        m = p.extra
                for p in ec['opposition']:
                    p.extra = p.voting_statistics.votes_per_seat()
                    if p.extra > m:
                        m = p.extra
                ec['friend_pages'][1][2] = True
                ec['norm_factor'] = m/20
                ec['baseline'] = 0
                ec['title'] = "%s" % (_('Parties'))

            if info=='discipline':
                m = 100
                for p in ec['coalition']:
                    p.extra = p.voting_statistics.discipline()
                    if p.extra < m:
                        m = p.extra
                for p in ec['opposition']:
                    p.extra = p.voting_statistics.discipline()
                    if p.extra < m:
                        m = p.extra
                ec['friend_pages'][2][2] = True
                ec['norm_factor'] = (100.0-m)/15
                ec['baseline'] = m - 2
                ec['title'] = "%s" % (_('Parties'))

            if info=='coalition-discipline':
                m = 100
                for p in ec['coalition']:
                    p.extra = p.voting_statistics.coalition_discipline()
                    if p.extra < m:
                        m = p.extra
                for p in ec['opposition']:
                    p.extra = p.voting_statistics.coalition_discipline()
                    if p.extra < m:
                        m = p.extra
                ec['friend_pages'][3][2] = True
                ec['norm_factor'] = (100.0-m)/15
                ec['baseline'] = m - 2
                ec['title'] = "%s" % (_('Parties'))


        return ListDetailView.render_list(self,request, queryset=qs, extra_context=ec, **kwargs)
