from datetime import date
from django.template import Context
from django.views.generic.list_detail import object_list, object_detail
from django.db.models import Count, Sum
from django.utils.translation import ugettext as _

from knesset.utils import limit_by_request
from knesset.mks.models import Member, Party
from knesset.hashnav.views import ListDetailView

from django.contrib.auth.decorators import login_required


member_context = dict (quesryset =
                       Member.objects.all(),
                      paginate_by = 20)

def member (request, pk=None):
    print "member view"
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


class MemberListView(ListDetailView):    
    def render_list(self,request, **kwargs):
        qs = self.queryset.all()
        info = request.GET.get('info','votes')
        ec = dict(self.extra_context) or {}
        if 'extra_context' in kwargs:
            ec.update(kwargs['extra_context'])
        ec['friend_pages'] = [['.?info=abc',_('By ABC'), False], ['.?info=votes', _('By number of votes'), False]]
        
        if info=='votes':
            qs = qs.annotate(extra=Count('votes')).order_by('-extra')
            ec['past_mks'] = ec['past_mks'].annotate(extra=Count('votes')).order_by('-extra')
            ec['friend_pages'][1][2] = True
            ec['norm_factor'] = float(qs[0].extra)/50
            ec['title'] = "%s %s" % (_('Members'), _('By number of votes'))
            return ListDetailView.render_list(self,request, queryset=qs, extra_context=ec, template_name='mks/member_list_with_bars.html', **kwargs)
        if info=='abc':
            ec['friend_pages'][0][2] = True
            ec['title'] = _('Members')
        return ListDetailView.render_list(self,request, queryset=qs, extra_context=ec, **kwargs)

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

