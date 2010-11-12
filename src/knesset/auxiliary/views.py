from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponseBadRequest
import random

from knesset.mks.models import Member
from knesset.laws.models import Vote,Bill
from tagging.models import Tag
from annotatetext.views import post_annotation as annotatetext_post_annotation
from annotatetext.models import Annotation

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
        context['tag'] = tags[random.randrange(len(tags))]
        context['annotations'] = Annotation.objects.all().order_by('timestamp').reverse()
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
