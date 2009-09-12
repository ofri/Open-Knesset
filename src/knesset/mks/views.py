from django.template import Context
from django.views.generic.list_detail import object_list, object_detail

from knesset.utils import limit_by_request
from knesset.mks.models import Member, Party

def member_list (request):
    qs = limit_by_request(Member.objects.all().order_by('name'), request)
    return object_list(request, queryset=qs)

def member_detail (request, pk):
    qs = Member.objects.filter(pk=pk)
    return object_detail(request, queryset=qs, object_id=pk, template_name='mks/member_detail.html')

def party_list (request):
    qs = limit_by_request(Party.objects.all().order_by('name'), request)
    return object_list(request, queryset=qs)

def party_detail (request, pk):
    qs = Party.objects.filter(pk=pk)
    return object_detail(request, queryset=qs, object_id=pk, template_name='mks/party_detail.html')
