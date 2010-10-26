#### encoding: cp1255 ####

import urllib2
import re
import logging
import csv
import datetime
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from knesset.mks.models import Member
from knesset.committees.models import Committee 
from knesset.events.models import Event

logger = logging.getLogger("open-knesset.parse_future_committee_meetings")
spamWriter = csv.writer(open('eggs.csv', 'wb'))

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
        for name, data in committee_data:
            date = date_re.findall(data)[0]
            year, month, day = int(date[2]), int(date[1]), int(date[0])
            
            meeting_datas = meeting_title_re.split(data)[1:]
            
            for meeting_data in meeting_datas:
                meeting_time = time_re.findall(meeting_data)[0]
                hour, minute = int(meeting_time[0]),int(meeting_time[1]) 
                meeting_agenda_data = meeting_agenda_re.split(meeting_data)[1] 
                titles = meeting_agenda_text_re.findall( meeting_agenda_data )
                titles = [ title.decode('cp1255').strip() for title in titles ]
                title = " ".join( titles )
    
                retval.append( [ name, year, month, day, hour, minute, title ] )
                spamWriter.writerow( [ name.encode('utf8'), year, month, day, hour, minute, title.encode('utf8') ] )
 
        return retval

    def update_future_committee_meetings_db(self,r):
        for row in r:
            try:
                committee = Committee.objects.get(name=row[0])
                ev, created = Event.objects.get_or_create( when = datetime.datetime( year=row[1], month=row[2], day=row[3], hour=row[4], minute=row[5], second=0 ),
                                                           what = row[6],
                                                           which_pk = committee.id,
                                                           which_type = self.committee_ct,
                                                           )
                print "new event at %s: %s" % (ev.when, ev.what)
            except Committee.DoesNotExist:
                logger.debug("couldn't find committee  %s" % row[0])
                try:
                    ev, created = Event.objects.get_or_create(when = datetime.datetime( year=row[1], month=row[2], day=row[3], hour=row[4], minute=row[5], second=0 ),
                                                               what = row[6],
                                                           )
                except Event.MultipleObjectsReturned:
                    created = False
            if created:
                logger.debug("created %s" % ev)
        
    def handle(self, *args, **options):
        r = self.parse_future_committee_meetings()
        logger.debug(r)
        self.update_future_committee_meetings_db(r)
