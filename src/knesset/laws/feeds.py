from django.utils.translation import ugettext as _
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from knesset.laws.models import Vote, Bill
from django.core.urlresolvers import reverse
class Votes(Feed):
    title = _("Knesset Votes feed")
    author_name = _("Open Knesset")
    # link = reverse('votes-feed')
    description = "Votes on Open Knesset website"

    def items(self):
        return Vote.objects.order_by('-time')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

class Bills(Feed):
    title = _("Knesset Bills feed")
    description = _("Bills from the Open Knesset site")

    def author_name(self):
        return _("Open Knesset")

    def link(self):
        return reverse('bills-feed')

    def get_object (self, request):
        ''' Not really getting the object here, just storing the requested 
            stages. 
        '''
        # BUG: there's probably reentrancy issues when one from this
        #      class is trying to serve 2 requests at almost the same time
        stages = request.GET.get('stage', False)
        self.stages = stages.split(',') if stages else False
        return None

    def items(self):
        bills = Bill.objects.order_by('-id')
        if self.stages:
            bills = bills.filter(stage__in = self.stages)
        return bills[:20]
