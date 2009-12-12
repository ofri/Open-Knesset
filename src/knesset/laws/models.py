from django.db import models
from knesset.mks.models import Member, Party
from tagging.models import Tag

from tagging.forms import TagField
from django import forms

VOTE_ACTION_TYPE_CHOICES = (
        (u'for', u'For'),
        (u'against', u'Against'),
        (u'abstain', u'Abstain'),
        (u'no-vote', u'No Vote'),
)

class VoteAction(models.Model):
    type   = models.CharField(max_length=10,choices=VOTE_ACTION_TYPE_CHOICES)
    member = models.ForeignKey('mks.Member')
    vote   = models.ForeignKey('Vote')
    def __unicode__(self):
        return "%s %s %s" % (self.member.name, self.type, self.vote.title)
 

class Vote(models.Model):
    meeting_number = models.IntegerField(null=True,blank=True)
    vote_number    = models.IntegerField(null=True,blank=True)    
    src_id         = models.IntegerField(null=True,blank=True)    
    src_url  = models.URLField(verify_exists=False, max_length=1024,null=True,blank=True)
    title          = models.CharField(max_length=1000)
    time           = models.DateTimeField(null=True,blank=True)
    time_string    = models.CharField(max_length=100)
    votes          = models.ManyToManyField('mks.Member', related_name='votes', blank=True, through='VoteAction')
    importance     = models.FloatField()
    summary        = models.TextField(null=True,blank=True)    
    full_text      = models.TextField(null=True,blank=True)
    full_text_url  = models.URLField(verify_exists=False, max_length=1024,null=True,blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.time_string)

    def get_voters_id(self, vote_type):
        return VoteAction.objects.filter(vote=self, type=vote_type).values_list('member__id', flat=True)

    def for_votes_count(self):
        return self.votes.filter(voteaction__type='for').count()

    def against_votes_count(self):
        return self.votes.filter(voteaction__type='against').count()

    def short_summary(self):
        if self.summary==None:
            return ''
        else:
            return self.summary[:60]

    def full_text_link(self):
        if self.full_text_url==None:
            return ''
        else:
            return '<a href="%s">link</a>' % self.full_text_url
    full_text_link.allow_tags = True  

    @models.permalink
    def get_absolute_url(self):
        return ('vote-detail', [str(self.id)])

    def _get_tags(self):
        return Tag.objects.get_for_object(self)

    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)

    tags = property(_get_tags, _set_tags)


    def tag_form(self):
        tf = TagForm()
        tf.tags = self.tags
        tf.initial = {'tags':','.join([str(t) for t in self.tags])}
        return tf

class TagForm(forms.Form):
    tags = TagField()
