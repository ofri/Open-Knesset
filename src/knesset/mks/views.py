from django.template import Context
from django.views.generic.list_detail import object_list, object_detail

from knesset.utils import limit_by_request
from knesset.mks.models import Member

def list (request):
    qs = limit_by_request(Member.objects.all().order_by('name'), request)
    return object_list(request, queryset=qs)

def detail (request, pk):
    qs = Member.objects.get(pk)
    return object_detail(request, queryset=qs, template_name='detail.html')
