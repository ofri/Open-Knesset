from django.db import models

from knesset.mks.models import Member

class Committee(models.Model):
    name = models.CharField(max_length=256)
    members = models.ManyToManyField('mks.Member', related_name='committees')
    def __unicode__(self):
        return "%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('committee-detail', [str(self.id)])
       

class CommitteeMeeting(models.Model):
    committee = models.ForeignKey(Committee)
    date_string = models.CharField(max_length=256)
    date = models.DateField()
    mks_attended = models.ManyToManyField('mks.Member', related_name='committee_meetings')
    votes_mentioned = models.ManyToManyField('laws.Vote', related_name='committee_meetings')
    protocol_text = models.TextField(null=True,blank=True)
    topics = models.TextField(null=True,blank=True)
    def __unicode__(self):
        return "%s %s" % (self.committee.name, self.date_string)
    
    @models.permalink
    def get_absolute_url(self):
        return ('committee-meeting', [str(self.id)])
  
