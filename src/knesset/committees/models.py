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

    class Meta:
        ordering = ('-date',)

    def __unicode__(self):
        return "%s %s" % (self.committee.name, self.date_string)
    
    @models.permalink
    def get_absolute_url(self):
        return ('committee-meeting', [str(self.id)])

    def save(self, **kwargs):
        super(CommitteeMeeting, self).save(**kwargs)
        self.parts.all().delete()

        # break the protocol to its parts
        # first, fix places where the colon is in the begining of next line 
        # (move it to the end of the correct line)
        protocol_text = []
        for line in self.protocol_text.split('\n'):
            if line.startswith(':'):
                protocol_text[-1] += ':'
                protocol_text.append(line[1:])                    
            else:
                protocol_text.append(line)

        i = 1
        section = []
        header = ''
            
        # now create the sections    
        for line in protocol_text:
            if line.endswith(':') and len(line)<40:
                if section:
                    ProtocolPart(meeting=self, order=i,
                        header=header, body='\n'.join(section)).save()
                i += 1
                header = line[:-1]
                section = []
            else:
                section.append (line)
                
        # don't forget the last section
        ProtocolPart(meeting=self, order=i,
            header=header, body='\n'.join(section)).save()

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
        if self.order == 1: 
            return self.meeting.get_absolute_url() 
        else: 
            return "%s#speech-%d-%d" % (self.meeting.get_absolute_url(),
                                        self.meeting.id, self.order)


@disable_for_loaddata
def handle_cm_save(sender, created, instance, **kwargs):
    cmct = ContentType.objects.get(app_label="committees", model="committeemeeting")
    mct = ContentType.objects.get(app_label="mks", model="member")
    for m in instance.mks_attended.all():
        if Action.objects.filter(actor_object_id=m.id, actor_content_type=mct, verb='attended', target_object_id=instance.id, 
                target_content_type=cmct).count()==0:    
            action.send(m, verb='attended', target=instance, description='committee meeting', timestamp=instance.date)
    
post_save.connect(handle_cm_save, sender=CommitteeMeeting)

