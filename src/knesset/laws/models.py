#encoding: utf-8
from datetime import date, timedelta
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.contrib.contenttypes import generic
from knesset.mks.models import Member, Party
from tagging.models import Tag, TaggedItem
from knesset.tagvotes.models import TagVote
from knesset.utils import disable_for_loaddata

from tagging.forms import TagField
from django import forms
from django.utils.translation import ugettext_lazy as _

VOTE_ACTION_TYPE_CHOICES = (
        (u'for', u'For'),
        (u'against', u'Against'),
        (u'abstain', u'Abstain'),
        (u'no-vote', u'No Vote'),
)


class PartyVotingStatistics(models.Model):
    party = models.OneToOneField('mks.Party',related_name='voting_statistics')

    def votes_against_party_count(self):
        return VoteAction.objects.filter(member__current_party=self.party, against_party=True).count()

    def votes_count(self):
        return VoteAction.objects.filter(member__current_party=self.party).exclude(type='no-vote').count()

    def votes_per_seat(self):
        return round(float(self.votes_count()) / self.party.number_of_seats,1)

    def discipline(self):
        total_votes = self.votes_count()
        votes_against_party = self.votes_against_party_count()
        return round(100.0*(total_votes-votes_against_party)/total_votes,1)

    def coalition_discipline(self): # if party is in opposition this actually returns opposition_discipline
        total_votes = self.votes_count()
        if self.party.is_coalition:
            votes_against_coalition = VoteAction.objects.filter(member__current_party=self.party, against_coalition=True).count()
        else:
            votes_against_coalition = VoteAction.objects.filter(member__current_party=self.party, against_opposition=True).count()
        return round(100.0*(total_votes-votes_against_coalition)/total_votes,1)

    def __unicode__(self):
        return "%s" % self.party.name

@disable_for_loaddata
def handle_party_save(sender, created, instance, **kwargs):
    if created:
        PartyVotingStatistics.objects.create(party=instance)
post_save.connect(handle_party_save, sender=Party)



class MemberVotingStatistics(models.Model):
    member = models.OneToOneField('mks.Member', related_name='voting_statistics')

    def votes_against_party_count(self, from_date = None):
        if from_date:
            return VoteAction.objects.filter(member=self.member, against_party=True, vote__time__gt=from_date).count()
        else:
            return VoteAction.objects.filter(member=self.member, against_party=True).count()

    def votes_count(self, from_date = None):
        if from_date:
            return VoteAction.objects.filter(member=self.member, vote__time__gt=from_date).exclude(type='no-vote').count()
        else:
            return VoteAction.objects.filter(member=self.member).exclude(type='no-vote').count()

    def average_votes_per_month(self):
        if hasattr(self, '_average_votes_per_month'):
            return self._average_votes_per_month
        st = self.member.service_time()
        if st:
                self._average_votes_per_month =  30.0*self.votes_count()/st
        else:
                self._average_votes_per_month = 0
        return self._average_votes_per_month

    def discipline(self, from_date = None):
        total_votes = self.votes_count(from_date)
        if total_votes <= 3: # not enough data
            return None
        votes_against_party = self.votes_against_party_count(from_date)
        return round(100.0*(total_votes-votes_against_party)/total_votes,1)

    def coalition_discipline(self, from_date = None): # if party is in opposition this actually returns opposition_discipline
        total_votes = self.votes_count(from_date)
        if total_votes <= 3: # not enough data
            return None
        if self.member.current_party.is_coalition:
            v = VoteAction.objects.filter(member=self.member, against_coalition=True)
        else:
            v = VoteAction.objects.filter(member=self.member, against_opposition=True)
        if from_date:
            v = v.filter(vote__time__gt=from_date)
        votes_against_coalition = v.count()
        return round(100.0*(total_votes-votes_against_coalition)/total_votes,1)


    def __unicode__(self):
        return "%s" % self.member.name

@disable_for_loaddata
def handle_mk_save(sender, created, instance, **kwargs):
    if created:
        MemberVotingStatistics.objects.create(member=instance)
post_save.connect(handle_mk_save, sender=Member)

class VoteAction(models.Model):
    type   = models.CharField(max_length=10,choices=VOTE_ACTION_TYPE_CHOICES)
    member = models.ForeignKey('mks.Member')
    vote   = models.ForeignKey('Vote')
    against_party = models.BooleanField(default=False)
    against_coalition = models.BooleanField(default=False)
    against_opposition = models.BooleanField(default=False)
    def __unicode__(self):
        return "%s %s %s" % (self.member.name, self.type, self.vote.title)

class VoteManager(models.Manager):
    # TODO: add i18n to the types so we'd have
    #   {'law-approve': _('approve law'), ...
    VOTE_TYPES = {'law-approve': u'אישור החוק', 'second-call': u'קריאה שנייה', 'demurrer': u'הסתייגות',
                  'no-confidence': u'הצעת אי-אמון', 'pass-to-committee': u'להעביר את ', 'continuation': u'להחיל דין רציפות'}

    def filter_and_order(self, *args, **kwargs):
        qs = self.all()
        filter_kwargs = {}
        if 'type' in kwargs and kwargs['type'] and kwargs['type'] != 'all':
            filter_kwargs['title__startswith'] = self.VOTE_TYPES[kwargs['type']]
        if 'since' in kwargs and kwargs['since'] and kwargs['since'] != 'all':
            filter_kwargs['time__gt'] = date.today()-timedelta(int(kwargs['since']))

        qs = qs.filter(**filter_kwargs) if filter_kwargs else qs

        if 'tagged' in kwargs and kwargs['tagged'] and kwargs['tagged'] == 'false':
            qs = qs.annotate(c=Count('tagged_items')).filter(c=0)
        if 'tagged' in kwargs and kwargs['tagged'] and kwargs['tagged'] == 'true':
            qs = qs.annotate(c=Count('tagged_items')).filter(c__gt=0)


        if 'order' in kwargs:
            if kwargs['order']=='controversy':
                qs = qs.filter(controversy__gt=0).order_by('-controversy')
            if kwargs['order']=='against-party':
                qs = qs.filter(against_party__gt=0).order_by('-against_party')
            if kwargs['order']=='votes':
                qs = qs.order_by('-votes_count')
        return qs

class Vote(models.Model):
    meeting_number = models.IntegerField(null=True,blank=True)
    vote_number    = models.IntegerField(null=True,blank=True)
    src_id         = models.IntegerField(null=True,blank=True)
    src_url  = models.URLField(verify_exists=False, max_length=1024,null=True,blank=True)
    title          = models.CharField(max_length=1000)
    time           = models.DateTimeField()
    time_string    = models.CharField(max_length=100)
    votes          = models.ManyToManyField('mks.Member', related_name='votes', blank=True, through='VoteAction')
    votes_count    = models.IntegerField(null=True, blank=True)
    importance     = models.FloatField()
    controversy    = models.IntegerField(null=True, blank=True)
    against_party  = models.IntegerField(null=True, blank=True)
    summary        = models.TextField(null=True,blank=True)
    full_text      = models.TextField(null=True,blank=True)
    full_text_url  = models.URLField(verify_exists=False, max_length=1024,null=True,blank=True)

    tagged_items = generic.GenericRelation(TaggedItem,
                                           object_id_field="object_id",
                                           content_type_field="content_type")


    objects = VoteManager()

    class Meta:
        ordering = ('-time',)
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')

    def __unicode__(self):
        return "%d %s (%s)" % (self.id, self.title, self.time_string)

    def get_voters_id(self, vote_type):
        return VoteAction.objects.filter(vote=self,
                         type=vote_type).values_list('member__id', flat=True)
    def for_votes(self):
        return VoteAction.objects.filter(vote=self, type='for')

    def for_votes_count(self):
        return self.for_votes().count()

    def against_votes(self):
        return VoteAction.objects.filter(vote=self, type='against')

    def against_votes_count(self):
        return self.against_votes().count()

    def against_party_votes(self):
        return self.votes.filter(voteaction__against_party=True)

    def against_party_votes_count(self):
        return self.against_party_votes().count()

    def against_coalition_votes(self):
        return self.votes.filter(voteaction__against_coalition=True)

    def against_coalition_votes_count(self):
        return self.against_coalition_votes.count()

    # TODO: this should die
    def against_opposition_votes_count(self):
        return VoteAction.objects.filter(vote=self, against_opposition=True).count()

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
        tags = Tag.objects.get_for_object(self)
        for t in tags:
            ti = TaggedItem.objects.filter(tag=t).filter(object_id=self.id)[0]
            t.score = sum(TagVote.objects.filter(tagged_item=ti).values_list('vote',flat=True))
            t.score_positive = t.score > 0
        tags = [t for t in tags]
        tags.sort(key=lambda x:-x.score)
        return tags

    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)

    tags = property(_get_tags, _set_tags)

    def tags_with_user_votes(self, user):
        tags = Tag.objects.get_for_object(self)
        for t in tags:
            ti = TaggedItem.objects.filter(tag=t).filter(object_id=self.id)[0]
            t.score = sum(TagVote.objects.filter(tagged_item=ti).values_list('vote',flat=True))
            v = TagVote.objects.filter(tagged_item=ti).filter(user=user)
            if(len(v)>0):
                t.user_score = v[0].vote
            else:
                t.user_score = 0
        return tags.sorted(cmp=lambda x,y:cmp(x.score, y.score))



    def tag_form(self):
        tf = TagForm()
        tf.tags = self.tags
        tf.initial = {'tags':', '.join([str(t) for t in self.tags])}
        return tf

class TagForm(forms.Form):
    tags = TagField()

class Law(models.Model):
    title = models.CharField(max_length=1000)
    
    def __unicode__(self):
        return self.title

    def merge(self, another_law):
        """ Merges another_law into this one 
            (move all pointers from another_law to self, then delete another_law
        """
        if another_law == self:
            return # don't accidentally delete myself by trying to merge.
        for pp in another_law.laws_privateproposal_related.all():
            pp.law = self
            pp.save()
        for kp in another_law.laws_knessetproposal_related.all():
            kp.law = self
            kp.save()
        another_law.delete()

class BillProposal(models.Model):
    knesset_id = models.IntegerField(blank=True, null=True)
    law = models.ForeignKey('Law', related_name="%(app_label)s_%(class)s_related", blank=True, null=True)
    title = models.CharField(max_length=1000)
    date = models.DateField(blank=True, null=True)    
    source_url = models.URLField(verify_exists=False, max_length=1024,null=True,blank=True)
    committee_meetings = models.ManyToManyField('committees.CommitteeMeeting', related_name="%(app_label)s_%(class)s_related", blank=True, null=True)
    votes = models.ManyToManyField('Vote', related_name="%(app_label)s_%(class)s_related", blank=True, null=True)
    class Meta:
        abstract = True


    def __unicode__(self):
        return u"%s %s" % (self.law, self.title)

class PrivateProposal(BillProposal):
    proposal_id = models.IntegerField(blank=True, null=True)
    proposers = models.ManyToManyField('mks.Member', related_name='bills', blank=True, null=True)
    joiners = models.ManyToManyField('mks.Member', related_name='bills_joined', blank=True, null=True)

class KnessetProposal(BillProposal):
    committee = models.ForeignKey('committees.Committee',related_name='bills', blank=True, null=True)
    booklet_number = models.IntegerField(blank=True, null=True)
    originals = models.ManyToManyField('PrivateProposal', related_name='knesset_proposals', blank=True, null=True)

