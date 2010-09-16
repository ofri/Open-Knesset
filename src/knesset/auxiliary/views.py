from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group
import random

from knesset.mks.models import Member
from knesset.laws.models import Vote,Bill
from tagging.models import Tag
from annotatetext.views import post_annotation as annotatetext_post_annotation

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
        cache.set('main_page_context', context, 300) # 5 Minutes
    template_name = '%s.%s%s' % ('main', settings.LANGUAGE_CODE, '.html')    
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def post_annotation(request):
    g = Group.objects.get(name='Valid Email')
    if g in request.user.groups.all():
        return annotatetext_post_annotation(request)
    else:
        return HttpResponseForbidden(_("Sorry, only users with validated email can annotate."))