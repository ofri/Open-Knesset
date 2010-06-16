#encoding: utf-8
from django.db.models.signals import post_save
from planet.models import Feed, Post
from actstream import action
from knesset.utils import cannonize, disable_for_loaddata
from knesset.laws.models import VoteAction
from knesset.links.models import Link, LinkType
from knesset.mks.models import Member

@disable_for_loaddata
def connect_feed(sender, created, instance, **kwargs):
    if created:
        t = cannonize(instance.title)
        rss_type = LinkType.objects.get(title='רסס')
        for m in Member.objects.all():
            if t.rfind(cannonize(m.name)) != -1:
                Link.objects.create(url=instance.url, title = instance.title,
                                    content_object=m, link_type=rss_type)
                print u'connected feed to %s' % m
                return
post_save.connect(connect_feed, sender=Feed)

@disable_for_loaddata
def record_vote_action(sender, created, instance, **kwargs):
    if created:
        action.send(instance.member, verb='voted',
                    description=instance.get_type_display(),
                    target = instance.vote,
                    timestamp=instance.vote.time)
post_save.connect(record_vote_action, sender=VoteAction)

@disable_for_loaddata
def record_post_action(sender, created, instance, **kwargs):
    if created:
        member = Link.objects.get(url=instance.feed.url).content_object
        action.send(member, verb='posted',
                    target = instance,
                    timestamp=instance.date_modified or instance.date_created)
post_save.connect(record_post_action, sender=Post)

