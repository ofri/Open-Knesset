from django.contrib.syndication.feeds import Feed
from django.contrib.comments.models import Comment

class Comments(Feed):
    title = "Open Knesset | Comments feed"
    link = "/comments/"
    description = "Comments on Open Knesset website"

    def items(self):
        return Comment.objects.order_by('-submit_date')[:20]

