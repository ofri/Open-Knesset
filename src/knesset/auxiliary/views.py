import random
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType

from knesset.mks.models import Member
from knesset.laws.models import Vote,Bill
from tagging.models import Tag
from annotatetext.views import post_annotation as annotatetext_post_annotation
from annotatetext.models import Annotation
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.contrib.comments.models import Comment

def main(request):
    context = cache.get('main_page_context')
    if not context:
        context = {}
        context['title'] = _('Home')
        context['member'] = Member.objects.all()[random.randrange(Member.objects.count())]
        votes = Vote.objects.filter_and_order(order='controversy')
        context['vote'] = votes[random.randrange(votes.count())]
        context['bill'] = Bill.objects.all()[random.randrange(Bill.objects.count())]
        tags = Tag.objects.cloud_for_model(Bill)
        context['tags'] = [random.choice(tags) for x in range(8)] if tags else None
        context['annotations'] = Annotation.objects.all().order_by('-timestamp')
        cache.set('main_page_context', context, 300) # 5 Minutes
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
        'lang' : lang,
        'cx': request.GET.get('cx')
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
