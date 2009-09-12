# Create your views here.
from django.views.generic.list_detail import object_list, object_detail
from django.conf import settings
from knesset.utils import limit_by_request
from knesset.laws.models import Vote

NUM_VOTES = getattr(settings, 'NUM_VOTES', 20)

def vote (request, pk=None):
    qs = Vote.objects.all()
    if pk:
        return object_detail(request, queryset=qs, object_id=pk, 
                             template_name='laws/vote.html')
    else:
        # TODO: move '20' to settings.
        qs = qs[:NUM_VOTES]
        return object_list(request, queryset=qs, 
                           template_name='laws/votes.html')
