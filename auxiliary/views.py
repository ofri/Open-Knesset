import csv, random, tagging, logging
from operator import attrgetter
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils import simplejson as json
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect, \
    HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, Http404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import BaseListView, ListView
from django.contrib.comments.models import Comment
from actstream import action
from actstream.models import Action
from mks.models import Member
from laws.models import Vote, Bill, get_debated_bills
from committees.models import Topic, CommitteeMeeting, PUBLIC_TOPIC_STATUS
from agendas.models import Agenda
from tagging.models import Tag, TaggedItem
from annotatetext.views import post_annotation as annotatetext_post_annotation
from annotatetext.models import Annotation
from knesset.utils import notify_responsible_adult, main_actions

logger = logging.getLogger("open-knesset.auxiliary.views")

def help_page(request):
    context = cache.get('help_page_context')
    if not context:
        context = {}
        context['title'] = _('Help')
        context['member'] = Member.current_knesset.all()[random.randrange(Member.current_knesset.count())]
        votes = Vote.objects.filter_and_order(order='controversy')
        context['vote'] = votes[random.randrange(votes.count())]
        context['bill'] = Bill.objects.all()[random.randrange(Bill.objects.count())]
        tags = Tag.objects.cloud_for_model(Bill)
        context['tags'] = random.sample(tags, min(len(tags),8)) if tags else None
        context['has_search'] = False # enable the base template search
        cache.set('help_page_context', context, 300) # 5 Minutes
    template_name = '%s.%s%s' % ('help_page', settings.LANGUAGE_CODE, '.html')
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def add_previous_comments(comments):
    previous_comments = set()
    for c in comments:
        c.previous_comments = Comment.objects.filter(
            object_pk=c.object_pk,
            content_type=c.content_type,
            submit_date__lt=c.submit_date).select_related('user')
        previous_comments.update(c.previous_comments)
        c.is_comment = True
    comments = [c for c in comments if c not in previous_comments]
    return comments

def get_annotations(comments, annotations):
    for a in annotations:
        a.submit_date = a.timestamp
    comments = add_previous_comments(comments)
    annotations.extend(comments)
    annotations.sort(key=lambda x:x.submit_date,reverse=True)
    return annotations

def main(request):
    """
    Note on annotations:
     Old:
        Return annotations by concatenating Annotation last 10 and Comment last
        10, adding all related comments (comments on same item that are older).
        annotations_old = get_annotations(
            annotations=list(Annotation.objects.all().order_by('-timestamp')[:10]),
            comments=Comment.objects.all().order_by('-submit_date')[:10])
     New:
        Return annotations by Action filtered to include only:
         annotation-added (to meeting), ignore annotated (by user)
         comment-added
    """
    #context = cache.get('main_page_context')
    #if not context:
    #    context = {
    #        'title': _('Home'),
    #        'hide_crumbs': True,
    #    }
    #    actions = list(main_actions()[:10])
    #
    #    annotations = get_annotations(
    #        annotations=[a.target for a in actions if a.verb != 'comment-added'],
    #        comments=[x.target for x in actions if x.verb == 'comment-added'])
    #    context['annotations'] = annotations
    #    b = get_debated_bills()
    #    if b:
    #        context['bill'] = get_debated_bills()[0]
    #    else:
    #        context['bill'] = None
    #    public_agenda_ids = Agenda.objects.filter(is_public=True
    #                                             ).values_list('id',flat=True)
    #    if len(public_agenda_ids) > 0:
    #        context['agenda_id'] = random.choice(public_agenda_ids)
    #    context['topics'] = Topic.objects.filter(status__in=PUBLIC_TOPIC_STATUS)\
    #                                     .order_by('-modified')\
    #                                     .select_related('creator')[:10]
    #    cache.set('main_page_context', context, 300) # 5 Minutes
    context = {
        'title': _('Home'),
        'hide_crumbs': True,
        'is_index': True,
    }
    template_name = '%s.%s%s' % ('main', settings.LANGUAGE_CODE, '.html')
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def post_annotation(request):
    if request.user.has_perm('annotatetext.add_annotation'):
        return annotatetext_post_annotation(request)
    else:
        return HttpResponseForbidden(_("Sorry, you do not have the permission to annotate."))

def search(request, lang='he'):

    # remove the 'cof' get variable from the query string so that the page
    # linked to by the javascript fallback doesn't think its inside an iframe.
    mutable_get = request.GET.copy()
    if 'cof' in mutable_get:
        del mutable_get['cof']

    return render_to_response('search/search.html', RequestContext(request, {
        'query': request.GET.get('q'),
        'query_string': mutable_get.urlencode(),
        'has_search': True,
        'lang': lang,
        'cx': settings.GOOGLE_CUSTOM_SEARCH,
    }))


def post_details(request, post_id):
    ''' patching django-planet's post_detail view so it would update the
        hitcount and redirect to the post's url
    '''
    from hitcount.views import _update_hit_count
    from hitcount.models import HitCount
    from planet.models import Post

    # update the it count
    ctype = ContentType.objects.get(app_label="planet", model="post")
    hitcount, created = HitCount.objects.get_or_create(content_type=ctype,
                                                  object_pk=post_id)
    result = _update_hit_count(request, hitcount)
    post = get_object_or_404(Post, pk=post_id)
    return HttpResponseRedirect(post.url)


class RobotsView(TemplateView):
    """Return the robots.txt"""

    template_name = 'robots.txt'

    def render_to_response(self, context, **kwargs):
        return super(RobotsView, self).render_to_response(context,
                        content_type='text/plain', **kwargs)


class AboutView(TemplateView):
    """About template"""

    template_name = 'about.html'


class CommentsView(ListView):
    """Comments index view"""

    model = Comment
    queryset = Comment.objects.order_by("-submit_date")

    paginate_by = 20

def _add_tag_to_object(user, app, object_type, object_id, tag):
    ctype = ContentType.objects.get_by_natural_key(app, object_type)
    (ti, created) = TaggedItem._default_manager.get_or_create(tag=tag, content_type=ctype, object_id=object_id)
    action.send(user,verb='tagged', target=ti, description='%s' % (tag.name))
    url = reverse('tag-detail', kwargs={'slug':tag.name})
    return HttpResponse("{'id':%d,'name':'%s', 'url':'%s'}" % (tag.id,tag.name,url))

@login_required
def add_tag_to_object(request, app, object_type, object_id):
    """add a POSTed tag_id to object_type object_id by the current user"""
    if request.method == 'POST' and 'tag_id' in request.POST: # If the form has been submitted...
        tag = get_object_or_404(Tag,pk=request.POST['tag_id'])
        return _add_tag_to_object(request.user, app, object_type, object_id, tag)

    return HttpResponseNotAllowed(['POST'])

@login_required
def remove_tag_from_object(request, app, object_type, object_id):
    """remove a POSTed tag_id from object_type object_id"""
    ctype = ContentType.objects.get_by_natural_key(app, object_type)
    if request.method == 'POST' and 'tag_id' in request.POST: # If the form has been submitted...
        tag = get_object_or_404(Tag,pk=request.POST['tag_id'])
        ti = TaggedItem._default_manager.filter(tag=tag, content_type=ctype, object_id=object_id)
        if len(ti)==1:
            logger.debug('user %s is deleting tagged item %d' % (request.user.username, ti[0].id))
            ti[0].delete()
            action.send(request.user,verb='removed-tag', target=ti[0], description='%s' % (tag.name))
        else:
            logger.debug('user %s tried removing tag %d from object, but failed, because len(tagged_items)!=1' % (request.user.username, tag.id))
    return HttpResponse("{'id':%d,'name':'%s'}" % (tag.id,tag.name))

@permission_required('tagging.add_tag')
def create_tag_and_add_to_item(request, app, object_type, object_id):
    """adds tag with name=request.POST['tag'] to the tag list, and tags the given object with it"""
    if request.method == 'POST' and 'tag' in request.POST:
        tag = request.POST['tag'].strip()
        msg = "user %s is creating tag %s on object_type %s and object_id %s".encode('utf8') % (request.user.username, tag, object_type, object_id)
        logger.info(msg)
        notify_responsible_adult(msg)
        if len(tag)<3:
            return HttpResponseBadRequest()
        tags = Tag.objects.filter(name=tag)
        if not tags:
            try:
                tag = Tag.objects.create(name=tag)
            except Exception:
                logger.warn("can't create tag %s" % tag)
                return HttpResponseBadRequest()
        if len(tags)==1:
            tag = tags[0]
        if len(tags)>1:
            logger.warn("More than 1 tag: %s" % tag)
            return HttpResponseBadRequest()
        return _add_tag_to_object(request.user, app, object_type, object_id, tag)
    else:
        return HttpResponseNotAllowed(['POST'])


def calculate_cloud_from_models(*args):
    from tagging.models import Tag
    cloud = Tag._default_manager.cloud_for_model(args[0])
    for model in args[1:]:
        for tag in Tag._default_manager.cloud_for_model(model):
            if tag in cloud:
                cloud[cloud.index(tag)].count+=tag.count
            else:
                cloud.append(tag)
    return tagging.utils.calculate_cloud(cloud)

class TagList(ListView):
    """Tags index view"""

    model = Tag
    template_name = 'auxiliary/tag_list.html'

    def get_queryset(self):
        return Tag.objects.all()

    def get_context_data(self, **kwargs):
        context = super(TagList, self).get_context_data(**kwargs)
        tags_cloud = calculate_cloud_from_models(Vote,Bill,CommitteeMeeting)
        tags_cloud.sort(key=lambda x:x.name)
        context['tags_cloud'] = tags_cloud
        return context

class TagDetail(DetailView):
    """Tags index view"""

    model = Tag
    template_name = 'auxiliary/tag_detail.html'
    slug_field = 'name'

    def create_tag_cloud(self, tag, limit=30):
        """
        Create tag could for tag <tag>. Returns only the <limit> most tagged members
        """

        try:
            mk_limit = int(self.request.GET.get('limit',limit))
        except ValueError:
            mk_limit = limit
        mk_taggeds = [b.proposers.all() for b in TaggedItem.objects.get_by_model(Bill, tag)]
        mk_taggeds += [v.votes.all() for v in TaggedItem.objects.get_by_model(Vote, tag)]
        mk_taggeds += [cm.mks_attended.all() for cm in TaggedItem.objects.get_by_model(CommitteeMeeting, tag)]
        d = {}
        for tagged in mk_taggeds:
            for p in tagged:
                d[p] = d.get(p,0)+1
        # now d is a dict: MK -> number of tagged in Bill, Vote and CommitteeMeeting in this tag
        mks = dict(sorted(d.items(),lambda x,y:cmp(y[1],x[1]))[:mk_limit])
        # Now only the most tagged are in the dict (up to the limit param)
        for mk in mks:
            mk.count = d[mk]
        mks = tagging.utils.calculate_cloud(mks)
        return mks

    def get_context_data(self, **kwargs):
        context = super(TagDetail, self).get_context_data(**kwargs)
        tag = context['object']
        bills_ct = ContentType.objects.get_for_model(Bill)
        bills = [ti.object for ti in
                    TaggedItem.objects.filter(tag=tag, content_type=bills_ct)]
        context['bills'] = bills
        votes_ct = ContentType.objects.get_for_model(Vote)
        votes = [ti.object for ti in
                    TaggedItem.objects.filter(tag=tag, content_type=votes_ct)]
        context['votes'] = votes
        cm_ct = ContentType.objects.get_for_model(CommitteeMeeting)
        cms = [ti.object for ti in
                    TaggedItem.objects.filter(tag=tag, content_type=cm_ct)]
        context['cms'] = cms
        context['members'] = self.create_tag_cloud(tag)
        return context

class CsvView(BaseListView):
    """A view which generates CSV files with information for a model queryset.
    Important class members to set when inheriting:
      * model -- the model to display information from.
      * queryset -- the query performed on the model; defaults to all.
      * filename -- the name of the resulting CSV file (e.g., "info.csv").
      * list_display - a list (or tuple) of tuples, where the first item in
        each tuple is the attribute (or the method) to display and
        the second item is the title of that column.

        The attribute can be a attribute on the CsvView child or the model
        instance itself. If it's a callable it'll be called with (obj, attr)
        for the CsvView attribute or without params for the model attribute.
    """

    filename = None
    list_display = None

    def dispatch(self, request):
        if None in (self.filename, self.list_display, self.model):
            raise Http404()
        self.request = request
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="{}"'.format(self.filename)

        object_list = self.get_queryset()
        self.prepare_csv_for_utf8(response)
        writer = csv.writer(response, dialect='excel')
        writer.writerow([title.encode('utf8')
                         for _, title in self.list_display])
        for obj in object_list:
            row = [self.get_display_attr(obj, attr)
                   for attr, _ in self.list_display]
            writer.writerow([unicode(item).encode('utf8') for item in row])
        return response

    def get_display_attr(self, obj, attr):
        """Return the display string for an attr, calling it if necessary."""
        display_attr =  getattr(self, attr, None)
        if display_attr is not None:
            if callable(display_attr):
                display_attr = display_attr(obj,attr)
        else:
            display_attr = getattr(obj, attr)
            if callable(display_attr):
                display_attr = display_attr()
        if display_attr is None:
            return ""
        return display_attr

    @staticmethod
    def prepare_csv_for_utf8(fileobj):
        """Prepend a byte order mark (BOM) to a file.

        When Excel opens a CSV file, it assumes the encoding is ASCII. The BOM
        directs it to decode the file with utf-8.
        """
        fileobj.write('\xef\xbb\xbf')


class GetMoreView(ListView):
    """A base view for feeding data to 'get more...' type of links

    Will return a json result, with partial of rendered template:
    {
        "content": "....",
        "current": current_patge number
        "total": total_pages
        "has_next": true if next page exists
    }
    We'll paginate the response. Since Get More link targets may already have
    initial data, we'll look for `initial` GET param, and take it into
    consdiration, completing to page size.
    """

    def get_context_data(self, **kwargs):
        ctx = super(GetMoreView, self).get_context_data(**kwargs)
        try:
            initial = int(self.request.GET.get('initial', '0'))
        except ValueError:
            initial = 0

        # initial only affects on first page
        if ctx['page_obj'].number > 1 or initial >= self.paginate_by - 1:
            initial = 0

        ctx['object_list'] = ctx['object_list'][initial:]
        return ctx

    def render_to_response(self, context, **response_kwargs):
        """We'll take the rendered content, and shove it into json"""

        tmpl_response = super(GetMoreView, self).render_to_response(
            context, **response_kwargs).render()

        page = context['page_obj']

        result = {
            'content': tmpl_response.content,
            'total': context['paginator'].num_pages,
            'current': page.number,
            'has_next': page.has_next(),
        }

        return HttpResponse(json.dumps(result, ensure_ascii=False),
                            content_type='application/json')
