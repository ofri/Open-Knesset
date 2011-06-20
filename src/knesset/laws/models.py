#encoding: utf-8
import itertools
import logging
from datetime import date, timedelta

from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes import generic
from django import forms
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag, TaggedItem
from tagging.forms import TagField
from actstream import Action
from actstream.models import action

from knesset.mks.models import Member, Party
from knesset.tagvotes.models import TagVote
from knesset.utils import disable_for_loaddata, slugify_name

logger = logging.getLogger("open-knesset.laws.models")
VOTE_ACTION_TYPE_CHOICES = (
        (u'for', _('For')),
        (u'against', _('Against')),
        (u'abstain', _('Abstain')),
        (u'no-vote', _('No Vote')),
)

CONVERT_TO_DISCUSSION_HEADERS = ('להעביר את הנושא'.decode('utf8'), 'העברת הנושא'.decode('utf8'))


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
        if total_votes > 0:
            votes_against_party = self.votes_against_party_count()
            return round(100.0*(total_votes-votes_against_party)/total_votes,1)
        else:
            return _('N/A')

    def coalition_discipline(self): # if party is in opposition this actually returns opposition_discipline
        total_votes = self.votes_count()
        if total_votes > 0:
            if self.party.is_coalition:
                votes_against_coalition = VoteAction.objects.filter(member__current_party=self.party, against_coalition=True).count()
            else:
                votes_against_coalition = VoteAction.objects.filter(member__current_party=self.party, against_opposition=True).count()
            return round(100.0*(total_votes-votes_against_coalition)/total_votes,1)
        else:
            return _('N/A')

    def __unicode__(self):
        return "%s" % self.party.name

@disable_for_loaddata
def handle_party_save(sender, created, instance, **kwargs):
    if created and instance._state.db=='default':
        pvs = PartyVotingStatistics(party=instance)
        pvs.save()
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
    if created and instance._state.db=='default':
        mvs = MemberVotingStatistics(member=instance)
        mvs.save()
post_save.connect(handle_mk_save, sender=Member)

class VoteAction(models.Model):
    type   = models.CharField(max_length=10,choices=VOTE_ACTION_TYPE_CHOICES)
    member = models.ForeignKey('mks.Member')
    vote   = models.ForeignKey('Vote')
    against_party = models.BooleanField(default=False)
    against_coalition = models.BooleanField(default=False)
    against_opposition = models.BooleanField(default=False)
    against_own_bill = models.BooleanField(default=False)
    def __unicode__(self):
        return "%s %s %s" % (self.member.name, self.type, self.vote.title)

@disable_for_loaddata
def record_vote_action(sender, created, instance, **kwargs):
    if created:
        action.send(instance.member, verb='voted',
                    description=instance.get_type_display(),
                    target = instance.vote,
                    timestamp=instance.vote.time)
post_save.connect(record_vote_action, sender=VoteAction)

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

        # In dealing with 'tagged' we use an ugly workaround for the fact that generic relations
        # don't work as expected with annotations.
        # please read http://code.djangoproject.com/ticket/10461 before trying to change this code
        if 'tagged' in kwargs and kwargs['tagged'] and kwargs['tagged'] == 'false':
            qs = qs.exclude(tagged_items__isnull=False)
        if 'tagged' in kwargs and kwargs['tagged'] and kwargs['tagged'] == 'true':
            untagged_ids = Vote.objects.exclude(tagged_items__isnull=False).values_list('id',flat=True)
            qs = qs.exclude(id__in=untagged_ids)


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
    importance     = models.FloatField(default=0.0)
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
        ordering = ('-time','-id')
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.time_string)

    @property
    def passed(self):
        return self.for_votes_count() > self.against_votes_count()

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
        return self.against_coalition_votes().count()

    # TODO: this should die
    def against_opposition_votes_count(self):
        return VoteAction.objects.filter(vote=self, against_opposition=True).count()

    def against_own_bill_votes(self):
        return self.votes.filter(voteaction__against_own_bill=True)

    def against_own_bill_votes_count(self):
        return self.against_own_bill_votes().count()

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

    def bills(self):
        "Return a list of all bills related to this vote"
        result = list(self.bills_pre_votes.all())
        result.extend(self.bills_first.all())
        b = Bill.objects.filter(approval_vote=self)
        if b:
            result.extend(b)
        return result

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
    merged_into = models.ForeignKey('Law', related_name='duplicates', blank=True, null=True)

    def __unicode__(self):
        return self.title

    def merge(self, another_law):
        """ Merges another_law into this one.
            Move all pointers from another_law to self,
            Then mark another_law as deleted by setting its merged_into field to self.
        """
        if another_law == self:
            return # don't accidentally delete myself by trying to merge.
        for pp in another_law.laws_privateproposal_related.all():
            pp.law = self
            pp.save()
        for kp in another_law.laws_knessetproposal_related.all():
            kp.law = self
            kp.save()
        for bill in another_law.bills.all():
            bill.law = self
            bill.save()
        another_law.merged_into = self
        another_law.save()

class BillProposal(models.Model):
    knesset_id = models.IntegerField(blank=True, null=True)
    law = models.ForeignKey('Law', related_name="%(app_label)s_%(class)s_related", blank=True, null=True)
    title = models.CharField(max_length=1000)
    date = models.DateField(blank=True, null=True)
    source_url = models.URLField(verify_exists=False, max_length=1024,null=True,blank=True)
    content_html = models.TextField(blank=True,default="")
    committee_meetings = models.ManyToManyField('committees.CommitteeMeeting', related_name="%(app_label)s_%(class)s_related", blank=True, null=True)
    votes = models.ManyToManyField('Vote', related_name="%(app_label)s_%(class)s_related", blank=True, null=True)
    class Meta:
        abstract = True

    def __unicode__(self):
        return u"%s %s" % (self.law, self.title)

    def get_absolute_url(self):
        if self.bill:
            return self.bill.get_absolute_url()
        else:
            return ""

class PrivateProposal(BillProposal):
    proposal_id = models.IntegerField(blank=True, null=True)
    proposers = models.ManyToManyField('mks.Member', related_name='bills_proposed', blank=True, null=True)
    joiners = models.ManyToManyField('mks.Member', related_name='bills_joined', blank=True, null=True)
    bill = models.ForeignKey('Bill', related_name='proposals',
                             blank=True, null=True)

class KnessetProposal(BillProposal):
    committee = models.ForeignKey('committees.Committee',related_name='bills', blank=True, null=True)
    booklet_number = models.IntegerField(blank=True, null=True)
    originals = models.ManyToManyField('PrivateProposal', related_name='knesset_proposals', blank=True, null=True)
    bill = models.OneToOneField('Bill', related_name='knesset_proposal',
                                 blank=True, null=True)

class GovProposal(BillProposal):
    booklet_number = models.IntegerField(blank=True, null=True)
    bill = models.OneToOneField('Bill', related_name='gov_proposal',
                                 blank=True, null=True)

BILL_STAGE_CHOICES = (
        (u'?', _(u'Unknown')),
        (u'1', _(u'Proposed')),
        (u'2', _(u'Pre-Approved')),
        (u'-2',_(u'Failed Pre-Approval')),
        (u'-2.1', _(u'Converted to discussion')),
        (u'3', _(u'In Committee')),
        (u'4', _(u'First Vote')),
        (u'-4',_(u'Failed First Vote')),
        (u'5', _(u'Committee Corrections')),
        (u'6', _(u'Approved')),
        (u'-6',_(u'Failed Approval')),
)

class Bill(models.Model):
    title = models.CharField(max_length=1000)
    full_title = models.CharField(max_length=2000, blank=True)
    slug = models.SlugField(max_length=1000)
    popular_name = models.CharField(max_length=1000, blank=True)
    popular_name_slug = models.CharField(max_length=1000, blank=True)
    law = models.ForeignKey('Law', related_name="bills", blank=True, null=True)
    stage = models.CharField(max_length=10,choices=BILL_STAGE_CHOICES)
    stage_date = models.DateField(blank=True, null=True) # date of entry to current stage
    pre_votes = models.ManyToManyField('Vote',related_name='bills_pre_votes', blank=True, null=True) # link to pre-votes related to this bill
    first_committee_meetings = models.ManyToManyField('committees.CommitteeMeeting',related_name='bills_first', blank=True, null=True) # CM related to this bill, *before* first vote
    first_vote = models.ForeignKey('Vote',related_name='bills_first', blank=True, null=True) # first vote of this bill
    second_committee_meetings = models.ManyToManyField('committees.CommitteeMeeting',related_name='bills_second', blank=True, null=True) # CM related to this bill, *after* first vote
    approval_vote = models.OneToOneField('Vote',related_name='bill_approved', blank=True, null=True) # approval vote of this bill
    proposers = models.ManyToManyField('mks.Member', related_name='bills', blank=True, null=True) # superset of all proposers of all private proposals related to this bill

    class Meta:
        verbose_name = _('Bill')
        verbose_name_plural = _('Bills')

    def __unicode__(self):
        return u"%s %s (%s)" % (self.law, self.title, self.get_stage_display())

    @models.permalink
    def get_absolute_url(self):
        return ('bill-detail', [str(self.id)])

    def save(self,**kwargs):
        self.slug = slugify_name(self.title)
        self.popular_name_slug = slugify_name(self.popular_name)
        super(Bill,self).save(**kwargs)
        for mk in self.proposers.all():
            mk.recalc_bill_statistics()

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


    def merge(self,another_bill):
        """Merges another_bill into self, and delete another_bill
        """
        if not(self.id):
            logger.debug('trying to merge into a bill with id=None, title=%s', self.title)
            self.save()
        if not(another_bill.id):
            logger.debug('trying to merge a bill with id=None, title=%s', another_bill.title)
            another_bill.save()

        if self==another_bill:
            logger.debug('abort merging bill %d into itself' % self.id)
            return
        logger.debug('merging bill %d into bill %d' % (another_bill.id, self.id))

        other_kp = KnessetProposal.objects.filter(bill=another_bill)
        my_kp = KnessetProposal.objects.filter(bill=self)
        if(len(my_kp) and len(other_kp)):
            logger.debug('abort merging bill %d into bill %d, because both have KPs' % (another_bill.id, self.id))
            return

        for pv in another_bill.pre_votes.all():
            self.pre_votes.add(pv)
        for cm in another_bill.first_committee_meetings.all():
            self.first_committee_meetings.add(cm)
        if not(self.first_vote) and another_bill.first_vote:
            self.first_vote = another_bill.first_vote
        for cm in another_bill.second_committee_meetings.all():
            self.second_committee_meetings.add(cm)
        if not(self.approval_vote) and another_bill.approval_vote:
            self.approval_vote = another_bill.approval_vote
        for m in another_bill.proposers.all():
            self.proposers.add(m)
        for pp in another_bill.proposals.all():
            pp.bill = self
            pp.save()
        if len(other_kp):
            other_kp[0].bill = self
            other_kp[0].save()
        another_bill.delete()
        self.update_stage()

    def update_votes(self):
        used_votes = [] # ids of votes already assigned 'roles', so we won't match a vote in 2 places
        gp = GovProposal.objects.filter(bill=self)
        if gp:
            gp = gp[0]
            for this_v in gp.votes.all():
                if (this_v.title.find('אישור'.decode('utf8')) == 0):
                    self.approval_vote = this_v
                    used_votes.append(this_v.id)
                if this_v.title.find('להעביר את'.decode('utf8')) == 0:
                    self.first_vote = this_v

        kp = KnessetProposal.objects.filter(bill=self)
        if len(kp):
            for this_v in kp[0].votes.all():
                if (this_v.title.find('אישור'.decode('utf8')) == 0):
                    self.approval_vote = this_v
                    used_votes.append(this_v.id)
                if this_v.title.find('להעביר את'.decode('utf8')) == 0:
                    if this_v.time.date() > kp[0].date:
                        self.first_vote = this_v
                    else:
                        self.pre_votes.add(this_v)
                    used_votes.append(this_v.id)
        pps = PrivateProposal.objects.filter(bill=self)
        if len(pps):
            for pp in pps:
                for this_v in pp.votes.all():
                    if this_v.id not in used_votes:
                        self.pre_votes.add(this_v)
        self.update_stage()


    def update_stage(self):
        """Updates the stage for this bill according to all current data
        """
        if self.approval_vote:
            if self.approval_vote.for_votes_count() > self.approval_vote.against_votes_count():
                self.stage = '6'
            else:
                self.stage = '-6'
            self.stage_date = self.approval_vote.time.date()
            self.save()
            return
        for cm in self.second_committee_meetings.all():
            if not(self.stage_date) or self.stage_date < cm.date:
                self.stage = '5'
                self.stage_date = cm.date
        if self.stage == '5':
            self.save()
            return
        if self.first_vote:
            if self.first_vote.for_votes_count() > self.first_vote.against_votes_count():
                self.stage = '4'
            else:
                self.stage = '-4'
            self.stage_date = self.first_vote.time.date()
            self.save()
            return
        try:
            kp = self.knesset_proposal
            if not(self.stage_date) or self.stage_date < kp.date:
                self.stage = '3'
                self.stage_date = kp.date
        except KnessetProposal.DoesNotExist:
            pass
        try:
            gp = self.gov_proposal
            if not(self.stage_date) or self.stage_date < gp.date:
                self.stage = '3'
                self.stage_date = gp.date
        except GovProposal.DoesNotExist:
            pass
        for cm in self.first_committee_meetings.all():
            if not(self.stage_date) or self.stage_date < cm.date:
                # if it was converted to discussion, seeing it in
                # a cm doesn't mean much.
                if self.stage != '-2.1':
                    self.stage = '3'
                    self.stage_date = cm.date
        for v in self.pre_votes.all():
            if not(self.stage_date) or self.stage_date < v.time.date():
                for h in CONVERT_TO_DISCUSSION_HEADERS:
                    if v.title.find(h)>=0:
                        self.stage = '-2.1' # converted to discussion
                        self.stage_date = v.time.date()
        for v in self.pre_votes.all():
            if not(self.stage_date) or self.stage_date < v.time.date():
                if v.for_votes_count() > v.against_votes_count():
                    self.stage = '2'
                else:
                    self.stage = '-2'
                self.stage_date = v.time.date()
        for pp in self.proposals.all():
            if not(self.stage_date) or self.stage_date < pp.date:
                self.stage = '1'
                self.stage_date = pp.date
        self.save()
        self.generate_activity_stream()

    def generate_activity_stream(self):
        ''' create an activity stream based on the data stored in self '''

        Action.objects.stream_for_actor(self).delete()
        ps = list(self.proposals.all())
        try:
            ps.append(self.gov_proposal)
        except GovProposal.DoesNotExist:
            pass

        for p in ps:
            action.send(self, verb='was-proposed', target=p,
                        timestamp=p.date, description=p.title)

        try:
            p = self.knesset_proposal
            action.send(self, verb='was-knesset-proposed', target=p,
                        timestamp=p.date, description=p.title)
        except KnessetProposal.DoesNotExist:
            pass

        for v in self.pre_votes.all():
            discussion = False
            for h in CONVERT_TO_DISCUSSION_HEADERS:
                if v.title.find(h)>=0: # converted to discussion
                    discussion = True
            if discussion:
                action.send(self, verb='was-converted-to-discussion', target=v,
                            timestamp=v.time)
            else:
                action.send(self, verb='was-pre-voted', target=v,
                            timestamp=v.time, description=v.passed)

        if self.first_vote:
            action.send(self, verb='was-first-voted', target=self.first_vote,
                        timestamp=self.first_vote.time, description=self.first_vote.passed)

        if self.approval_vote:
            action.send(self, verb='was-approval-voted', target=self.approval_vote,
                        timestamp=self.approval_vote.time, description=self.approval_vote.passed)

        for cm in self.first_committee_meetings.all():
            action.send(self, verb='was-discussed-1', target=cm,
                        timestamp=cm.date, description=cm.committee.name)

        for cm in self.second_committee_meetings.all():
            action.send(self, verb='was-discussed-2', target=cm,
                        timestamp=cm.date, description=cm.committee.name)

        for g in self.gov_decisions.all():
            action.send(self, verb='was-voted-on-gov', target=g,
                        timestamp=g.date, description=str(g.stand))



class GovLegislationCommitteeDecision(models.Model):
    title = models.CharField(max_length=1000)
    subtitle = models.TextField(null=True,blank=True)
    text = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    source_url = models.URLField(verify_exists=False, max_length=1024,null=True,blank=True)
    bill = models.ForeignKey('Bill', blank=True, null=True, related_name='gov_decisions')
    stand = models.IntegerField(blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return u"%s" % (self.title)
    
    def get_absolute_url(self):
        return self.bill.get_absolute_url()

from listeners import *
