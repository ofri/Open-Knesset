# encoding: utf-8
import re
import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.text import truncate_words
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from tagging.models import Tag
from annotatetext.models import Annotation
from knesset.events.models import Event

COMMITTEE_PROTOCOL_PAGINATE_BY = 400

logger = logging.getLogger("open-knesset.committees.models")

    
class Committee(models.Model):
    name = models.CharField(max_length=256)
    members = models.ManyToManyField('mks.Member', related_name='committees')
    chairpersons = models.ManyToManyField('mks.Member', related_name='chaired_committees')
    replacements = models.ManyToManyField('mks.Member', related_name='replacing_in_committees')
    events = generic.GenericRelation(Event, content_type_field="which_type",
       object_id_field="which_pk")
    agenda_topics = models.ManyToManyField('topics.Topic', related_name='committees', through="AgendaTopic")

    def __unicode__(self):
        return "%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('committee-detail', [str(self.id)])

    @property
    def annotations(self):
        protocol_part_tn = ProtocolPart._meta.db_table
        meeting_tn = CommitteeMeeting._meta.db_table
        committee_tn = Committee._meta.db_table
        annotation_tn = Annotation._meta.db_table
        protocol_part_ct = ContentType.objects.get_for_model(ProtocolPart)
        ret = Annotation.objects.filter(content_type=protocol_part_ct)
        return ret.extra(tables = [protocol_part_tn,
                    meeting_tn, committee_tn],
                    where = [ "%s.object_id=%s.id" % (annotation_tn, protocol_part_tn),
                              "%s.meeting_id=%s.id" % (protocol_part_tn, meeting_tn),
                              "%s.committee_id=%%s" % meeting_tn],
                    params = [ self.id ]).distinct()

    def members_by_presence(self):
        members = []
        for m in (self.members.all()|
                  self.chairpersons.all()|
                  self.replacements.all()).distinct():
            m.meetings_count = \
                100 * m.committee_meetings.filter(committee=self).count() \
                / self.meetings.count()
            members.append(m)
        members.sort(key=lambda x:x.meetings_count, reverse=True)
        return members

    def recent_meetings(self):
        return self.meetings.all().order_by('-date')[:10]

    def get_public_topics(self):
        return AgendaTopic.objects.filter(committee=self, status__in=(PUBLIC_AGENDA_ITEM_STATUS))

not_header = re.compile(r'(^אני )|((אלה|אלו|יבוא|מאלה|ייאמר|אומר|אומרת|נאמר|כך|הבאים|הבאות):$)|(\(.\))|(\(\d+\))|(\d\.)'.decode('utf8'))
def legitimate_header(line):
    """Retunrs true if 'line' looks like something should should be a protocol part header"""
    if not(line.endswith(':')) or len(line)>50 or not_header.search(line):
        return False
    return True

class CommitteeMeeting(models.Model):
    committee = models.ForeignKey(Committee, related_name='meetings')
    # TODO: do we really need a date string? can't we just format date?
    date_string = models.CharField(max_length=256)
    date = models.DateField()
    mks_attended = models.ManyToManyField('mks.Member', related_name='committee_meetings')
    votes_mentioned = models.ManyToManyField('laws.Vote', related_name='committee_meetings', blank=True)
    protocol_text = models.TextField(null=True,blank=True)
    topics = models.TextField(null=True,blank=True)
    src_url  = models.URLField(verify_exists=False, max_length=1024,null=True,blank=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = _('Committee Meeting')
        verbose_name_plural = _('Committee Meetings')

    def title (self):
        return truncate_words (self.topics, 12)

    def __unicode__(self):
        return (u"%s - %s" % (self.committee.name,
                                self.title())).replace("&nbsp;", u"\u00A0")

    @models.permalink
    def get_absolute_url(self):
        return ('committee-meeting', [str(self.id)])

    def _get_tags(self):
        tags = Tag.objects.get_for_object(self)
        return tags

    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)

    tags = property(_get_tags, _set_tags)

    def save(self, **kwargs):
        super(CommitteeMeeting, self).save(**kwargs)

    def create_protocol_parts(self, delete_existing=False):
        """ Create protocol parts from this instance's protocol_text
            Optionally, delete existing parts.
            If the meeting already has parts, and you don't ask to
            delete them, a ValidationError will be thrown, because
            it doesn't make sense to create the parts again.
        """
        if delete_existing:
            ppct = ContentType.objects.get_for_model(ProtocolPart)
            annotations = Annotation.objects.filter(content_type=ppct, object_id__in=self.parts.all)
            logger.debug('deleting %d annotations, because I was asked to delete the relevant protocol parts on cm.id=%d' % (annotations.count(), self.id))
            annotations.delete()
            self.parts.all().delete()
        else:
            if self.parts.count():
                raise ValidationError('CommitteeMeeting already has parts. delete them if you want to run create_protocol_parts again.')

        if not self.protocol_text: # sometimes there are empty protocols
            return # then we don't need to do anything here.

        # break the protocol to its parts
        # first, fix places where the colon is in the begining of next line
        # (move it to the end of the correct line)
        protocol_text = []
        for line in re.sub("[ ]+"," ", self.protocol_text).split('\n'):
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
            if legitimate_header(line):
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
    speaker = models.ForeignKey('persons.Person', blank=True, null=True, related_name='protocol_parts')
    objects = ProtocolPartManager()

    annotatable = True

    def get_absolute_url(self):
        if self.order == 1:
            return self.meeting.get_absolute_url()
        else:
            page_num = 1 + (self.order-1)/COMMITTEE_PROTOCOL_PAGINATE_BY
            if page_num==1: # this is on first page
                return "%s#speech-%d-%d" % (self.meeting.get_absolute_url(),
                                            self.meeting.id, self.order)
            else:
                return "%s?page=%d#speech-%d-%d" % (self.meeting.get_absolute_url(),
                                                    page_num,
                                                    self.meeting.id, self.order)

    def __unicode__(self):
        return "%s %s: %s" % (self.meeting.committee.name, self.header,
                              self.header)

AGENDA_ITEM_PUBLISHED, AGENDA_ITEM_FLAGGED, AGENDA_ITEM_REJECTED,\
AGENDA_ITEM_ACCEPTED, AGENDA_ITEM_APPEAL = range(5)
PUBLIC_AGENDA_ITEM_STATUS = ( AGENDA_ITEM_PUBLISHED, AGENDA_ITEM_ACCEPTED)

class AgendaItemManager(models.Manager):
    def get_public(self):
        return self.filter(status__in=PUBLIC_AGENDA_ITEM_STATUS)

class AgendaTopic(models.Model):
    '''
        AgendaTopic is used to hold the latest event about a topic and a committee

        Fields:
            created - the time a topic was first connected to a committee
            modified - last time the status or the message was updated
            editor - the user that entered the data
            status - the current status
            message - a message explaining the status change
    '''

    topic = models.ForeignKey('topics.Topic')
    committee = models.ForeignKey(Committee, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    editor = models.ForeignKey(User)
    status = models.IntegerField(choices = (
        (AGENDA_ITEM_PUBLISHED, _('published')),
        (AGENDA_ITEM_FLAGGED, _('flagged')),
        (AGENDA_ITEM_REJECTED, _('rejected')),
        (AGENDA_ITEM_ACCEPTED, _('accepted')),
        (AGENDA_ITEM_APPEAL, _('appeal')),
            ), default=AGENDA_ITEM_PUBLISHED)
    message = models.TextField(default="")

    objects = AgendaItemManager()

    def set_status(self, status, message=''):
       self.status = status
       self.message = message
       self.save()

    def __unicode__(self):
        return "%s: %s" % (self.get_status_display(), unicode(self.topic))

from listeners import *
