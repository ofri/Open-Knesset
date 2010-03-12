#encoding: utf-8
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _
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

from knesset.hashnav.views import ListDetailView

from datetime import date, timedelta
from django.db.models import Count
import urllib
import urllib2

class VoteListView(ListDetailView):
    
    vote_types = {'law-approve': u'אישור החוק', 'second-call': u'קריאה שנייה', 'demurrer': u'הסתייגות', 
                  'no-confidence': u'הצעת אי-אמון', 'pass-to-committee': u'להעביר את ', 'continuation': u'להחיל דין רציפות'}

    def render_list(self,request, **kwargs):
        qs = self.queryset.all()
        vt = request.GET.get('vote_type','all')
        if vt in self.vote_types:
            qs = qs.filter(title__startswith=self.vote_types[vt])            

        if request.GET.get('time','all') != 'all':
            try:
                num_days = int(request.GET['time'])
                qs = qs.filter(time__gt=date.today()-timedelta(num_days))
                if num_days==7: time='week'
                if num_days==30: time='month'
            except ValueError: # not a number
                pass
        if 'order' in request.GET:
            if request.GET['order']=='controversy':
                qs = qs.filter(controversy__gt=0).order_by('-controversy')
            if request.GET['order']=='against-party':
                qs = qs.filter(against_party__gt=0).order_by('-against_party')
            if request.GET['order']=='votes':
                qs = qs.order_by('-votes_count')
        if not self.extra_context: self.extra_context = {}

        friend_page = {}
        friend_page['vote_type'] = urllib.quote(request.GET.get('vote_type','all').encode('utf8'))
        friend_page['time'] = urllib.quote(request.GET.get('time','all').encode('utf8'))
        friend_page['order'] = urllib.quote(request.GET.get('order','time').encode('utf8'))

        friend_pages = [
            ('vote_type','all',_('All votes')),
            ('vote_type','law-approve', _('Law Approvals')),
            ('vote_type','second-call', _('Second Call')),
            ('vote_type','demurrer', _('Demurrer')),
            ('vote_type','no-confidence', _('Motion of no confidence')),
            ('vote_type','pass-to-committee', _('Pass to committee')),
            ('vote_type','continuation', _('Continuation')),
            ('time','7',_('Last Week')),
            ('time','30',_('Last Month')),
            ('time','all',_('All times')),
            ('order','time',_('Time')),
            ('order','controversy', _('Controversy')),
            ('order','against-party',_('Against Party')),
            ('order','votes',_('Number of votes'))
        ]

        r = {}

        for key, value, name in friend_pages:
            page = friend_page.copy()
            current = False
            if page[key]==value:
                current = True
            else:
                page[key] = value
            url =  "./?%s" % urllib.urlencode(page)
            if key not in r:
                r[key] = []
            r[key].append((url, name, current))        

        #[(_('all'),'&'.join([time,order])), (_('law approval'))],[],[]]        
        self.extra_context['friend_pages'] = r            
        return ListDetailView.render_list(self,request, queryset=qs, **kwargs)

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

