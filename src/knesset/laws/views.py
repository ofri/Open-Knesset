# Create your views here.
from django.views.generic.list_detail import object_list, object_detail
from django.conf import settings
from knesset.utils import limit_by_request
from knesset.laws.models import Vote
from django.http import HttpResponseRedirect
from knesset.laws.models import TagForm
from tagging.models import Tag, TaggedItem
from knesset.tagvotes.models import TagVote


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

def vote_on_tag(request,object_id,tag_id,vote):
    v = Vote.objects.get(pk=object_id)
    ti = TaggedItem.objects.filter(tag__id=tag_id).filter(object_id=v.id)[0]
    (tv, created) = TagVote.objects.get_or_create(tagged_item=ti, user=request.user, defaults={'vote': 0})
    tv.vote = vote
    tv.save()
    return HttpResponseRedirect("/vote/%s" % object_id)
