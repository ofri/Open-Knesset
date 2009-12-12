# Create your views here.
from django.views.generic.list_detail import object_list, object_detail
from django.conf import settings
from knesset.utils import limit_by_request
from knesset.laws.models import Vote
from django.http import HttpResponseRedirect
from knesset.laws.models import TagForm

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

def submit_tags(request,object_id):
    if request.method == 'POST': # If the form has been submitted...
        form = TagForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            v = Vote.objects.get(pk=object_id)
            v.tags = form.cleaned_data['tags'].replace('"','')


    return HttpResponseRedirect("/vote/%s" % object_id)
