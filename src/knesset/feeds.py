from django.contrib.syndication.feeds import Feed
from django.contrib.comments.models import Comment
from knesset.laws.models import Vote, Bill

class Comments(Feed):
    title = "Open Knesset | Comments feed"
    link = "/comments/"
    description = "Comments on Open Knesset website"

    def items(self):
        return Comment.objects.order_by('-submit_date')[:20]


class Votes(Feed):
    title = "Open Knesset | Votes feed"
    link = "/votes/"
    description = "Votes on Open Knesset website"

    def items(self):
        return Vote.objects.order_by('-time')[:20]


class Bills(Feed):
    title = "Open Knesset | Bills feed"
    link = "/bills/"
    description = "Bills on Open Knesset website"

    def items(self):
        return Bill.objects.order_by('-id')[:20]


