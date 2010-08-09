from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.conf import settings

import random

from knesset.mks.models import Member
from knesset.laws.models import Vote,Bill
from tagging.models import Tag

def main(request):
    title = _('Home')
    member = Member.objects.all()[random.randrange(Member.objects.count())]
    votes = Vote.objects.filter_and_order(order='controversy')
    vote = votes[random.randrange(votes.count())]
    bill = Bill.objects.all()[random.randrange(Bill.objects.count())]
    tags = Tag.objects.cloud_for_model(Bill)
    tag = tags[random.randrange(len(tags))]
    template_name = '%s.%s%s' % ('main', settings.LANGUAGE_CODE, '.html')    
    return render_to_response(template_name,
        {"title":title, "member":member, "vote":vote, "bill":bill, "tag":tag},
        context_instance=RequestContext(request))

