#encoding: utf-8
from django.utils.translation import ugettext_lazy
from django.views.generic.list_detail import object_list, object_detail
from django.conf import settings
from knesset.utils import limit_by_request
from knesset.laws.models import Vote
from django.http import HttpResponseRedirect
from knesset.laws.models import TagForm
from tagging.models import Tag, TaggedItem
from knesset.tagvotes.models import TagVote

from django.http import Http404
from tagging.views import tagged_object_list




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
            v.tags = u'%s,' % form.cleaned_data['tags'].replace('"',u'”') # add comma in the end to force treatment as comma-separated list
                                                                          # replace " with ” to support hebrew initials


    return HttpResponseRedirect("/vote/%s" % object_id)

def vote_on_tag(request,object_id,tag_id,vote):
    v = Vote.objects.get(pk=object_id)
    ti = TaggedItem.objects.filter(tag__id=tag_id).filter(object_id=v.id)[0]
    (tv, created) = TagVote.objects.get_or_create(tagged_item=ti, user=request.user, defaults={'vote': 0})
    tv.vote = vote
    tv.save()
    return HttpResponseRedirect("/vote/%s" % object_id)

def tagged(request,tag):
    title = ugettext_lazy('Votes tagged %(tag)s') % {'tag': tag}
    try:
        return tagged_object_list(request, queryset_or_model = Vote, tag=tag, extra_context={'title':title})
    except Http404:
        return object_list(request, queryset=Vote.objects.none(), extra_context={'title':title})

