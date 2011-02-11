from django.utils.translation import ugettext as _
from django.contrib.syndication.views import Feed
from django.contrib.comments.models import Comment
from django.shortcuts import get_object_or_404
from knesset.laws.models import Vote, Bill

class Comments(Feed):
    title = "%s | %s" %(_("Open Knesset"), _("Comments feed"))
    link = "/comments/"
    description = "Comments on Open Knesset website"

    def items(self):
        return Comment.objects.order_by('-submit_date')[:20]


class Votes(Feed):
    title = "%s | %s" %(_("Open Knesset"), _("Votes feed"))
    link = "/votes/"
    description = "Votes on Open Knesset website"

    def items(self):
        return Vote.objects.order_by('-time')[:20]


class Bills(Feed):
    title = "%s | %s" %(_("Open Knesset"), _("Bills feed"))
    link = "/bills/"
    description = "Bills on Open Knesset website"

    def get_object (self, request, *args, **kwargs):
        stages = request.GET.get('stages', False)
        #TODO: there's probably a re-entrancy issue with self.stages
        self.stages = stages.split(',') if stages else False
        return super(Bills,self).get_object(request, *args, **kwargs)

    def items(self):
        bills = Bill.objects.order_by('-id')
        if self.stages:
            bills = bills.filter(stage__in = self.stages)
        return bills[:20]
