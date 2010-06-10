from django.db.models.signals import post_save
from planet.models import Feed
from knesset.utils import cannonize, disable_for_loaddata
from knesset.laws.models import VoteAction

@disable_for_loaddata
def connect_feed(sender, created, instance, **kwargs):
    if created:
        t = cannonize(instance.title)
        for m in Member.objects.all():
            if t.rfind(cannonize(m.name)) != -1:
                Link.objects.create(url=instance.url, title = instance.title, content_object=m)
                print u'connected feed to %s' % m
                return
post_save.connect(connect_feed, sender=Feed)

@disable_for_loaddata
def record_vote_action(sender, created, instance, **kwargs):
    from actstream import action
    if created:
        action.send(instance.member, verb='voted',
                    description=instance.type,
                    target = instance,
                    timestamp=instance.vote.time)
post_save.connect(record_vote_action, sender=VoteAction)

