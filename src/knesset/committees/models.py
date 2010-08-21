from django.db import models

from knesset.mks.models import Member

from django.db.models.signals import post_save
from knesset.utils import disable_for_loaddata
from actstream import action
from actstream.models import Action
from django.contrib.contenttypes.models import ContentType

class Committee(models.Model):
    name = models.CharField(max_length=256)
    members = models.ManyToManyField('mks.Member', related_name='committees')
    def __unicode__(self):
        return "%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('committee-detail', [str(self.id)])
       
class CommitteeMeeting(models.Model):
    committee = models.ForeignKey(Committee, related_name='meetings')
    # TODO: do we really need a date string? can't we just format date?
    date_string = models.CharField(max_length=256)
    date = models.DateField()
    mks_attended = models.ManyToManyField('mks.Member', related_name='committee_meetings')
    votes_mentioned = models.ManyToManyField('laws.Vote', related_name='committee_meetings', blank=True)
    protocol_text = models.TextField(null=True,blank=True)
    topics = models.TextField(null=True,blank=True)
    def __unicode__(self):
        return "%s %s" % (self.committee.name, self.date_string)
    
    @models.permalink
    def get_absolute_url(self):
        return ('committee-meeting', [str(self.id)])
  
    class Meta:
        ordering = ('-date',)

class ProtocolPartManager(models.Manager):
    def list(self):
        return self.order_by("order")

class ProtocolPart(models.Model):
    meeting = models.ForeignKey(CommitteeMeeting, related_name='parts')
    order = models.IntegerField()
    header = models.TextField(blank=True)
    body = models.TextField(blank=True)

    objects = ProtocolPartManager()

    annotatable = True

    def get_absolute_url(self): 
        if self.ordernr == 1: 
            return self.mmeting.get_absolute_url() 
        else: 
            return self.mmeting.get_absolute_url()+"-%d" % self.ordernr 


@disable_for_loaddata
def handle_cm_save(sender, created, instance, **kwargs):
    cmct = ContentType.objects.get(app_label="committees", model="committeemeeting")
    mct = ContentType.objects.get(app_label="mks", model="member")
    for m in instance.mks_attended.all():
        if Action.objects.filter(actor_object_id=m.id, actor_content_type=mct, verb='attended', target_object_id=instance.id, 
                target_content_type=cmct).count()==0:    
            action.send(m, verb='attended', target=instance, description='committee meeting', timestamp=instance.date)
    
post_save.connect(handle_cm_save, sender=CommitteeMeeting)

