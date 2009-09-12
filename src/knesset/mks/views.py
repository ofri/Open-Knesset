from django.template import Context
from django.views.generic.list_detail import object_list, object_detail

from knesset.utils import limit_by_request, yearstart
from knesset.mks.models import Member, Party

def member (request, pk=None):
    qs = Member.objects.all()
    if pk:
        return object_detail(request, queryset=qs, object_id=pk, 
                             template_name='mks/member.html')
    else:
        qs = qs.filter(end_date__gte=yearstart(2009))
        return object_list(request, queryset=qs, 
                           template_name='mks/members.html')

def party (request, pk=None):
    qs = Party.objects.all()
    if pk:
        return object_detail(request, queryset=qs, object_id=pk, 
                             template_name='mks/party_detail.html')
    else:
        # return a list
        qs = limit_by_request(qs, request)
        return object_list(request, queryset=qs)
