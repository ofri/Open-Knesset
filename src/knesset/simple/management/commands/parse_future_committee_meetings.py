#### encoding: cp1255 ####

from collections import namedtuple
import urllib2
import re
import logging
import csv
import datetime
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from dateutil import zoneinfo

from mks.models import Member
from committees.models import Committee
from events.models import Event

# NB: All dates scraped from the knesset site are assumed to be in timezone Israel.
isr_tz = zoneinfo.gettz('Israel')
utc_tz = zoneinfo.gettz('UTC')

logger = logging.getLogger("open-knesset.parse_future_committee_meetings")
spamWriter = csv.writer(open('eggs.csv', 'wb'))

ParsedResult = namedtuple('ParseResult',
    'name, year, month, day, hour, minute, '
   +'title, end_hour, end_minute, end_guessed')

class Command(BaseCommand):

    args = ''
    help = 'Parses commitee members from the Knesset website'
    committee_ct = ContentType.objects.get_for_model(Committee)

    def parse_future_committee_meetings(self):
        retval = []

        url = 'http://knesset.gov.il/agenda/heb/CommitteesByDate.asp'

        data = urllib2.urlopen(url).read()

        committee_re = re.compile('<td class="Day" bgcolor="#990000" >\s+\xf1\xe3\xf8 \xe4\xe9\xe5\xed \xec.+, <span style=color:#c0c0c0>')
        committee_name = re.compile('<td class="Day" bgcolor="#990000" >\s+\xf1\xe3\xf8 \xe4\xe9\xe5\xed \xec(.+), <span style=color:#c0c0c0>')
        date_re = re.compile("<nobr>\((\d+)/(\d+)/(\d+)\)</nobr>")
        time_re = re.compile('\xe1\xf9\xf2\xe4&nbsp;(\d\d):(\d\d)')
        meeting_title_re = re.compile('TitleCommittee')
        meeting_agenda_re = re.compile('class="Agenda"')
        meeting_agenda_text_re = re.compile('<[Tt]d class=AgendaText>([^<]+)</[Tt]d>')

        datas = committee_re.split( data )[1:]

        committee_names = committee_name.findall( data )
        committee_names = [ name.decode('cp1255') for name in committee_names ]

        committee_data = zip( committee_names, datas )
        def parse_meeting_data(meeting_data):
            meeting_time = time_re.findall(meeting_data)[0]
            hour, minute = int(meeting_time[0]), int(meeting_time[1])
            meeting_agenda_data = meeting_agenda_re.split(meeting_data)[1]
            titles = meeting_agenda_text_re.findall( meeting_agenda_data )
            titles = [ title.decode('cp1255').strip() for title in titles ]
            title = " ".join( titles )
            # XXX Note the + 2 HACK:
            # because knesset.gov lacks information on the expected end of the last
            # meeting in any committees daily schedule. NOTE: we can guess a little better (use
            # lunch for instance, or look for members other meetings)
            return ParsedResult(name=name, year=year, month=month,
                                 day=day, hour=hour, minute=minute, title=title,
                                 end_hour=hour + 2, end_minute=minute,
                                 end_guessed=True)
        for name, data in committee_data:
            date = date_re.findall(data)[0]
            year, month, day = int(date[2]), int(date[1]), int(date[0])

            meeting_datas = meeting_title_re.split(data)[1:]

            for i, meeting_data in enumerate(meeting_datas):
                parsed = parse_meeting_data(meeting_data)
                if i > 0:
                    last = retval[-1]
                    # ugly, but it's a tuple, can't assign
                    new_last = ParsedResult(
                        name=last.name, year=last.year, month=last.month,
                        day=last.day, hour=last.hour, minute=last.minute,
                        title=last.title,
                        end_hour=parsed.hour,
                        end_minute=parsed.minute,
                        end_guessed=False)
                    retval[-1] = new_last
                retval.append(parsed)

        # since this is now a two pass, kinda, do the logging after.
        for p in retval:
            spamWriter.writerow( [ p.name.encode('utf8'), p.year, p.month,
                                   p.day, p.hour, p.minute, p.end_hour,
                                   p.end_minute, p.end_guessed,
                                   p.title.encode('utf8') ] )
        return retval

    def update_future_committee_meetings_db(self, r):
        for p in r:
            try:
                committee = Committee.objects.get(name=p.name)
                when_over = datetime.datetime(
                    year=p.year, month=p.month, day=p.day, hour=p.end_hour,
                    minute=p.end_minute, second=0, tzinfo=isr_tz).astimezone(utc_tz)
                when = datetime.datetime(
                    year=p.year, month=p.month, day=p.day, hour=p.hour,
                    minute=p.minute, second=0, tzinfo=isr_tz).astimezone(utc_tz)
                ev, created = Event.objects.get_or_create( when = when,
                                                           when_over = when_over,
                                                           when_over_guessed = p.end_guessed,
                                                           where = unicode(committee),
                                                           what = p.title,
                                                           which_pk = committee.id,
                                                           which_type = self.committee_ct,
                                                           )
                logger.debug("new event at %s - %s%s: %s" % (ev.when, ev.when_over,
                                                             '' if not ev.when_over_guessed else '(guess)',
                                                             ev.what))
            except Committee.DoesNotExist:
                logger.debug("couldn't find committee  %s" % p.name)
                try:
                    ev, created = Event.objects.get_or_create(
                        when = datetime.datetime( year=p.year, month=p.month,
                                                  day=p.day, hour=p.hour,
                                                  minute=p.minute, second=0 ),
                                                  what=p.title)
                except Event.MultipleObjectsReturned:
                    created = False
            if created:
                logger.debug("created %s" % ev)

    def handle(self, *args, **options):
        logger.debug('Events objects count before update: %d' % Event.objects.count())
        r = self.parse_future_committee_meetings()
        logger.debug(r)
        self.update_future_committee_meetings_db(r)
        logger.debug('Events objects count after update: %d' % Event.objects.count())
