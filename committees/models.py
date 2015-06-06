# encoding: utf-8
import re
import logging
import sys
import traceback
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.text import Truncator
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from tagging.models import Tag, TaggedItem
from djangoratings.fields import RatingField
from annotatetext.models import Annotation
from events.models import Event
from links.models import Link
from plenum.create_protocol_parts import create_plenum_protocol_parts
from mks.models import Knesset
from lobbyists.models import LobbyistHistory, LobbyistCorporation
from itertools import groupby
from hebrew_numbers import gematria_to_int

COMMITTEE_PROTOCOL_PAGINATE_BY = 120

logger = logging.getLogger("open-knesset.committees.models")

class Committee(models.Model):
    name = models.CharField(max_length=256)
    # comma separated list of names used as name aliases for harvesting
    aliases = models.TextField(null=True,blank=True)
    members = models.ManyToManyField('mks.Member', related_name='committees', blank=True)
    chairpersons = models.ManyToManyField('mks.Member', related_name='chaired_committees', blank=True)
    replacements = models.ManyToManyField('mks.Member', related_name='replacing_in_committees', blank=True)
    events = generic.GenericRelation(Event, content_type_field="which_type",
       object_id_field="which_pk")
    description = models.TextField(null=True,blank=True)
    portal_knesset_broadcasts_url = models.URLField(max_length=1000, blank=True)
    type = models.CharField(max_length=10, default='committee')

    @property
    def gender_presence(self):
        # returns a touple of (female_presence, male_presence
        r={'F': 0, 'M': 0}
        for cm in self.meetings.all():
            try:
                results = groupby(cm.mks_attended.all(), lambda mk: mk.gender)
            except ValueError:
                continue
            for i in results:
                key, count = i[0], len(list(i[1]))
                r[key] += count
        return r['F'], r['M']

    def __unicode__(self):
        if self.type == 'plenum':
            return "%s" % ugettext('Plenum')
        else:
            return "%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        if self.type == 'plenum':
            return 'plenum', []
        else:
            return 'committee-detail', [str(self.id)]

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

    def members_by_presence(self, ids=None):
        """Return the members with computed presence percentage.
        If ids is not provided, this will return committee members. if ids is
        provided, this will return presence data for the given members.
        """
        def count_percentage(res_set, total_count):
            return (100 * res_set.count() / total_count) if total_count else 0

        def filter_this_year(res_set):
            return res_set.filter(date__gte='%d-01-01' % datetime.now().year)

        if ids is not None:
            members = list(Member.objects.filter(id__in=ids))
        else:
            members = list((self.members.filter(is_current=True) |
                            self.chairpersons.all() |
                            self.replacements.all()).distinct())

        d = Knesset.objects.current_knesset().start_date
        meetings_with_mks = self.meetings.filter(
            mks_attended__isnull=False).distinct()
        all_meet_count = meetings_with_mks.filter(
            date__gte=d).count()
        year_meet_count = filter_this_year(meetings_with_mks).count()
        for m in members:
            all_member_meetings = m.committee_meetings.filter(committee=self,
                                                              date__gte=d)
            year_member_meetings = filter_this_year(all_member_meetings)
            m.meetings_percentage = count_percentage(all_member_meetings,
                                                     all_meet_count)
            m.meetings_percentage_year = count_percentage(year_member_meetings,
                                                          year_meet_count)

        members.sort(key=lambda x: x.meetings_percentage, reverse=True)
        return members

    def recent_meetings(self):
        return self.meetings.all().order_by('-date')[:10]

    def future_meetings(self):
        cur_date = datetime.now()
        return self.events.filter(when__gt=cur_date)

    def get_knesset_id(self):
        """
            return the id of the committee on the knesset website,
            update this if any committee id is changed in the db.
            the knesset committee id list is fixed and includes all committes ever.
        """

        trans = {  #key is our id, val is knesset id
            1: '1',  #כנסת
            2: '3',  #כלכלה
            3: '27',  #עליה
            4: '5',  #הפנים
            5: '6',  #החוקה
            6: '8',  #החינוך
            7: '10',  #ביקורת המדינה
            8: '13',  #מדע
            9: '2',  #כספים
            10: '28',  #עבודה
            11: '11',  #מעמד האישה
            12: '15',  #עובדים זרים
            13: '33',  #משנה סחר בנשים
            14: '19',  #פניות הציבור
            15: '25',  #זכויות הילד
            16: '12',  #סמים
            17: '266',  #עובדים ערבים
            18: '321',  #משותפת סביבה ובריאות
        }

        try:
            return trans[self.pk]
        except KeyError:
            logger.error('Committee %d missing knesset id' % self.pk)
            return None

not_header = re.compile(r'(^אני )|((אלה|אלו|יבוא|מאלה|ייאמר|אומר|אומרת|נאמר|כך|הבאים|הבאות):$)|(\(.\))|(\(\d+\))|(\d\.)'.decode('utf8'))
def legitimate_header(line):
    """Returns true if 'line' looks like something should be a protocol part header"""
    if re.match(r'^\<.*\>\W*$',line): # this is a <...> line.
        return True
    if not(line.strip().endswith(':')) or len(line)>50 or not_header.search(line):
        return False
    return True

class CommitteeMeetingManager(models.Manager):

    def filter_and_order(self, *args, **kwargs):
        qs = self.all()
        # In dealing with 'tagged' we use an ugly workaround for the fact that generic relations
        # don't work as expected with annotations.
        # please read http://code.djangoproject.com/ticket/10461 before trying to change this code
        if kwargs.get('tagged'):
            if kwargs['tagged'] == ['false']:
                qs = qs.exclude(tagged_items__isnull=False)
            elif kwargs['tagged'] != ['all']:
                qs = qs.filter(tagged_items__tag__name__in=kwargs['tagged'])

        if kwargs.get('to_date'):
            qs = qs.filter(time__lte=kwargs['to_date']+timedelta(days=1))

        if kwargs.get('from_date'):
            qs = qs.filter(time__gte=kwargs['from_date'])

        return qs.select_related('committee')

class CommitteeMeeting(models.Model):
    committee = models.ForeignKey(Committee, related_name='meetings')
    date_string = models.CharField(max_length=256)
    date = models.DateField(db_index=True)
    mks_attended = models.ManyToManyField('mks.Member', related_name='committee_meetings')
    votes_mentioned = models.ManyToManyField('laws.Vote', related_name='committee_meetings', blank=True)
    protocol_text = models.TextField(null=True,blank=True)
    topics = models.TextField(null=True,blank=True)
    src_url  = models.URLField(max_length=1024,null=True,blank=True)
    tagged_items = generic.GenericRelation(TaggedItem,
                                           object_id_field="object_id",
                                           content_type_field="content_type")
    lobbyists_mentioned = models.ManyToManyField('lobbyists.Lobbyist', related_name='committee_meetings')
    lobbyist_corporations_mentioned = models.ManyToManyField('lobbyists.LobbyistCorporation', related_name='committee_meetings')

    objects = CommitteeMeetingManager()

    class Meta:
        ordering = ('-date',)
        verbose_name = _('Committee Meeting')
        verbose_name_plural = _('Committee Meetings')

    def title (self):
        truncator = Truncator(self.topics)
        return truncator.words(12)

    def __unicode__(self):
        cn = cache.get('committee_%d_name' % self.committee_id)
        if not cn:
            if self.committee.type=='plenum':
                cn='Plenum'
            else:
                cn = unicode(self.committee)
            cache.set('committee_%d_name' % self.committee_id,
                      cn,
                      settings.LONG_CACHE_TIME)
        if cn=='Plenum':
            return (u"%s" % (self.title())).replace("&nbsp;", u"\u00A0")
        else:
            return (u"%s - %s" % (cn,
                                self.title())).replace("&nbsp;", u"\u00A0")

    @models.permalink
    def get_absolute_url(self):
        if self.committee.type=='plenum':
            return ('plenum-meeting', [str(self.id)])
        else:
            return ('committee-meeting', [str(self.id)])

    def _get_tags(self):
        tags = Tag.objects.get_for_object(self)
        return tags

    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)

    tags = property(_get_tags, _set_tags)

    def save(self, **kwargs):
        super(CommitteeMeeting, self).save(**kwargs)

    def create_protocol_parts(self, delete_existing=False, mks=None, mk_names=None):
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

        if self.committee.type=='plenum':
            create_plenum_protocol_parts(self, mks=mks, mk_names=mk_names)
            return

        # break the protocol to its parts
        # first, fix places where the colon is in the beginning of next line
        # (move it to the end of the correct line)
        protocol_text = []
        for line in re.sub("[ ]+"," ", self.protocol_text).split('\n'):
            #if re.match(r'^\<.*\>\W*$',line): # this line start and ends with
            #                                  # <...>. need to remove it.
            #    line = line[1:-1]
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
                if (i>1)or(section):
                    ProtocolPart(meeting=self, order=i,
                        header=header, body='\n'.join(section)).save()
                i += 1
                header = re.sub('[\>:]+$', '', re.sub('^[\< ]+', '', line))
                section = []
            else:
                section.append(line)

        # don't forget the last section
        ProtocolPart(meeting=self, order=i, header=header, body='\n'.join(section)).save()

    def redownload_plenum_protocol(self):
        """utility method to redownload plenum meeting protocol"""
        from plenum.management.commands.parse_plenum_protocols_subcommands.download import download_for_existing_meeting
        download_for_existing_meeting(self)

    def reparse_plenum_protocol(self):
        self.redownload_plenum_protocol()
        from plenum.management.commands.parse_plenum_protocols_subcommands.parse import parse_for_existing_meeting
        parse_for_existing_meeting(self)

    @property
    def plenum_meeting_number(self):
        res = None
        parts = self.parts.filter(body__contains=u'ישיבה')
        if parts.count() > 0:
            r = re.search(u'ישיבה (.*)$', self.parts.filter(body__contains=u'ישיבה').first().body)
            if r:
                res = gematria_to_int(r.groups()[0])
        return res

    def plenum_link_votes(self):
        from laws.models import Vote
        if self.plenum_meeting_number:
            for vote in Vote.objects.filter(meeting_number=self.plenum_meeting_number):
                for part in self.parts.filter(header__contains=u'הצבעה'):
                    r = re.search(r' (\d+)$', part.header)
                    if r and vote.vote_number == int(r.groups()[0]):
                        url = part.get_absolute_url()
                        Link.objects.get_or_create(
                            object_pk=vote.pk,
                            content_type=ContentType.objects.get_for_model(Vote),
                            url = url,
                            defaults = {
                                'title': u'לדיון בישיבת המליאה'
                            }
                        )

    def get_bg_material(self):
        """
            returns any background material for the committee meeting, or [] if none
        """
        import urllib2
        from BeautifulSoup import BeautifulSoup

        time = re.findall(r'(\d\d:\d\d)',self.date_string)[0]
        date = self.date.strftime('%d/%m/%Y')
        cid = self.committee.get_knesset_id()
        if cid is None:  # missing this committee knesset id
            return []  # can't get bg material

        url = 'http://www.knesset.gov.il/agenda/heb/material.asp?c=%s&t=%s&d=%s' % (cid,time,date)
        data = urllib2.urlopen(url)
        bg_links = []
        if data.url == url: #if no bg material exists we get redirected to a different page
            bgdata = BeautifulSoup(data.read()).findAll('a')

            for i in bgdata:
                bg_links.append( {'url': 'http://www.knesset.gov.il'+i['href'], 'title': i.string})

        return bg_links

    @property
    def bg_material(self):
        return Link.objects.filter(object_pk=self.id,
                    content_type=ContentType.objects.get_for_model(CommitteeMeeting).id)

    def find_attending_members(self, mks, mk_names):
        try:
            r = re.search("חברי הו?ועדה(.*?)(\n[^\n]*(ייעוץ|יועץ|רישום|רש(מים|מות|מו|מ|מת|ם|מה)|קצר(נים|ניות|ן|נית))[\s|:])".decode('utf8'), self.protocol_text, re.DOTALL).group(1)
            s = r.split('\n')
            for (i, name) in enumerate(mk_names):
                if not mks[i].party_at(self.date):  # not a member at time of
                                                    # this meeting?
                    continue  # then don't search for this MK.
                for s0 in s:
                    if s0.find(name) >= 0:
                        self.mks_attended.add(mks[i])
        except Exception:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            logger.debug("%s%s",
                         ''.join(traceback.format_exception(exceptionType,
                                                            exceptionValue,
                                                            exceptionTraceback)
                                ),
                         '\nCommitteeMeeting.id=' + str(self.id))
        logger.debug('meeting %d now has %d attending members' % (
            self.id,
            self.mks_attended.count()))

    @cached_property
    def main_lobbyist_corporations_mentioned(self):
        ret = []
        for corporation in self.lobbyist_corporations_mentioned.all():
            main_corporation = corporation.main_corporation
            if main_corporation not in ret:
                ret.append(main_corporation)
        for lobbyist in self.main_lobbyists_mentioned:
            corporation = LobbyistCorporation.objects.get(id=lobbyist.cached_data['latest_corporation']['id'])
            if corporation not in ret and corporation.main_corporation == corporation:
                ret.append(corporation)
        return ret

    @cached_property
    def main_lobbyists_mentioned(self):
        return self.lobbyists_mentioned.all()


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
    type = models.TextField(blank=True,max_length=20)

    annotatable = True

    class Meta:
        ordering = ('order','id')

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

TOPIC_PUBLISHED, TOPIC_FLAGGED, TOPIC_REJECTED,\
TOPIC_ACCEPTED, TOPIC_APPEAL, TOPIC_DELETED = range(6)
PUBLIC_TOPIC_STATUS = ( TOPIC_PUBLISHED, TOPIC_ACCEPTED)

class TopicManager(models.Manager):
    ''' '''
    get_public = lambda self: self.filter(status__in=PUBLIC_TOPIC_STATUS)

    by_rank = lambda self: self.extra(select={
            'rank': '((100/%s*rating_score/(1+rating_votes+%s))+100)/2' % (Topic.rating.range, Topic.rating.weight)
            }).order_by('-rank')

    def summary(self, order='-rank'):
        return self.filter(status__in=PUBLIC_TOPIC_STATUS).extra(select={
            'rank': '((100/%s*rating_score/(1+rating_votes+%s))+100)/2' % (Topic.rating.range, Topic.rating.weight)
            }).order_by(order)
        #TODO: rinse it so this will work
        return self.get_public().by_rank()


class Topic(models.Model):
    '''
        Topic is used to hold the latest event about a topic and a committee

        Fields:
            title - the title
            description - its description
            created - the time a topic was first connected to a committee
            modified - last time the status or the message was updated
            editor - the user that entered the data
            status - the current status
            log - a text log that keeps text messages for status changes
            committees - defined using a many to many from `Committee`
    '''

    creator = models.ForeignKey(User)
    editors = models.ManyToManyField(User, related_name='editing_topics', null=True, blank=True)
    title = models.CharField(max_length=256,
                             verbose_name = _('Title'))
    description = models.TextField(blank=True,
                                   verbose_name = _('Description'))
    status = models.IntegerField(choices = (
        (TOPIC_PUBLISHED, _('published')),
        (TOPIC_FLAGGED, _('flagged')),
        (TOPIC_REJECTED, _('rejected')),
        (TOPIC_ACCEPTED, _('accepted')),
        (TOPIC_APPEAL, _('appeal')),
        (TOPIC_DELETED, _('deleted')),
            ), default=TOPIC_PUBLISHED)
    rating = RatingField(range=7, can_change_vote=True, allow_delete=True)
    links = generic.GenericRelation(Link, content_type_field="content_type",
       object_id_field="object_pk")
    events = generic.GenericRelation(Event, content_type_field="which_type",
       object_id_field="which_pk")
    # no related name as `topics` is already defined in CommitteeMeeting as text
    committees = models.ManyToManyField(Committee,
                                        verbose_name = _('Committees'))
    meetings = models.ManyToManyField(CommitteeMeeting, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    log = models.TextField(default="", blank=True)

    class Meta:
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
    @models.permalink
    def get_absolute_url(self):
        return ('topic-detail', [str(self.id)])

    def __unicode__(self):
        return "%s" % self.title

    objects = TopicManager()

    def set_status(self, status, message=''):
       self.status = status
       self.log = '\n'.join((u'%s: %s' % (self.get_status_display(), datetime.now()),
                            u'\t%s' % message,
                            self.log,)
                           )
       self.save()

    def can_edit(self, user):
        return user.is_superuser or user==self.creator or \
               user in self.editors.all()


from listeners import *
