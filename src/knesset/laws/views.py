#encoding: utf-8
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list, object_detail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from knesset.utils import limit_by_request
from knesset.laws.models import Vote
from django.http import HttpResponseRedirect, HttpResponse
from knesset.laws.models import TagForm
from tagging.models import Tag, TaggedItem
from knesset.tagvotes.models import TagVote

from django.http import Http404
from tagging.views import tagged_object_list

from knesset.hashnav.views import ListDetailView

from django.db.models import Count
import urllib
import urllib2

class VoteListView(ListDetailView):

    session_votes_key = 'selected_votes'
    
    friend_pages = [
            ('vote_type','all',_('All votes')),
            ('vote_type','law-approve', _('Law Approvals')),
            ('vote_type','second-call', _('Second Call')),
            ('vote_type','demurrer', _('Demurrer')),
            ('vote_type','no-confidence', _('Motion of no confidence')),
            ('vote_type','pass-to-committee', _('Pass to committee')),
            ('vote_type','continuation', _('Continuation')),
            ('tagged','all',_('All')),
            ('tagged','false',_('Untagged Votes')),
            ('tagged','true',_('Tagged Votes')),            
            ('time','7',_('Last Week')),
            ('time','30',_('Last Month')),
            ('time','all',_('All times')),
            ('order','time',_('Time')),
            ('order','controversy', _('Controversy')),
            ('order','against-party',_('Against Party')),
            ('order','votes',_('Number of votes')),
            
        ]

    def pre (self, request, **kwargs):

        pass
        

    def render_list(self,request, **kwargs):

        
        if not self.extra_context: self.extra_context = {}

        saved_selection = request.session.get(self.session_votes_key, dict())
        options = {
            'type': request.GET.get('vote_type', saved_selection.get('vote_type', None)),
            'since': request.GET.get('time', saved_selection.get('time',None)),
            'order': request.GET.get('order', saved_selection.get('order', None)),
            'tagged': request.GET.get('tagged', saved_selection.get('tagged', None)),
        }
        
        queryset = Vote.objects.filter_and_order(**options)
        
        friend_page = {}
        friend_page['vote_type'] = urllib.quote(request.GET.get('vote_type',saved_selection.get('vote_type','all')).encode('utf8'))
        friend_page['tagged'] = urllib.quote(request.GET.get('tagged', saved_selection.get('tagged','all')).encode('utf8'))
        friend_page['time'] = urllib.quote(request.GET.get('time', saved_selection.get('time','all')).encode('utf8'))
        friend_page['order'] = urllib.quote(request.GET.get('order',saved_selection.get('order','time')).encode('utf8'))

        request.session[self.session_votes_key] = friend_page
        
        r = {}

        for key, value, name in self.friend_pages:
            page = friend_page.copy()
            current = False
            if page[key]==value:
                current = True
                if key=='vote_type':
                    self.extra_context['title'] = name
            else:
                page[key] = value
            url =  "./?%s" % urllib.urlencode(page)
            if key not in r:
                r[key] = []
            r[key].append((url, name, current))        

        #[(_('all'),'&'.join([time,order])), (_('law approval'))],[],[]]        
        self.extra_context['friend_pages'] = r
        show_stands = request.GET.get('show_stands', None)            
        if show_stands:
            show_stands = show_stands.split(',')
        else:
            selected_mks = request.session.get('selected_mks',dict())
            show_stands = [str(i) for i in selected_mks.keys()]
        self.extra_context['show_stands'] = show_stands
        return super(VoteListView, self).render_list(request, queryset=queryset, **kwargs)

@login_required
def submit_tags(request,object_id):
    if request.method == 'POST': # If the form has been submitted...
        form = TagForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            v = Vote.objects.get(pk=object_id)
            v.tags = u'%s,' % form.cleaned_data['tags'].replace('"',u'”') # add comma in the end to force treatment as comma-separated list
                                                                          # replace " with ” to support hebrew initials


    return HttpResponseRedirect("/vote/%s" % object_id)

@login_required
def suggest_tag(request,object_id):
    if request.method == 'POST' and 'tag_id' in request.POST: # If the form has been submitted...
        v = Vote.objects.get(pk=object_id)
        tag = Tag.objects.get(pk=request.POST['tag_id'])
        ctype = ContentType.objects.get_for_model(v)
        (ti, created) = TaggedItem._default_manager.get_or_create(tag=tag, content_type=ctype, object_id=object_id)
        (tv, created) = TagVote.objects.get_or_create(tagged_item=ti, user=request.user, defaults={'vote': 0})
        tv.vote = +1
        tv.save()
    return HttpResponse("OK")



@login_required
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

