# encoding: utf-8
import logging, re
from django.core.management.base import NoArgsCommand
from django.db.models import Q
from committees.models import CommitteeMeeting,ProtocolPart
from mks.models import Member
from persons.models import Person,PersonAlias

logger = logging.getLogger("open-knesset.persons.create_persons")

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):

        # Find persons in all protocol parts:
        p = Person.objects.all()
        names_and_aliases = zip([x.name for x in p],p)
        p = PersonAlias.objects.all()
        names_and_aliases.extend(zip([x.name for x in p],[x.person for x in p]))
        names_and_aliases.sort(key=lambda x:len(x[0]), reverse=True)
        for pp_header in set(ProtocolPart.objects.exclude(header='').values_list('header',flat=True)):                
            for (name,person) in names_and_aliases:
                if pp_header.find(name)>=0:
                    parts_updated = ProtocolPart.objects.filter(header=pp_header).update(speaker=person)                    
                    print "updated speaker for %d parts to %s" % (parts_updated,person.name)
                    if person.mk:
                        cm_ids = set(ProtocolPart.objects.filter(header=pp_header).values_list('meeting__id',flat=True))
                        for cm in CommitteeMeeting.objects.filter(id__in=cm_ids):
                            cm.mks_attended.add(person.mk)
                    break
        
        # find mks in the presence protocol part. this is needed for MKs that don't talk.
        mk_names = []
        mks = []
        mk_persons = Person.objects.filter(mk__isnull=False)
        mks.extend([person.mk for person in mk_persons])
        mk_aliases = PersonAlias.objects.filter(person__in=mk_persons)
        mk_names.extend(mk_persons.values_list('name',flat=True))
        mk_names.extend(mk_aliases.values_list('name',flat=True))
        mks.extend([alias.person.mk for alias in mk_aliases])

        title = 'חברי הוועדה'.decode('utf-8')
        for part in ProtocolPart.objects.filter(header=title):
            for (i,name) in enumerate(mk_names):
                for line in part.body.split('\n'):
                    if line.find(name)>=0:
                        part.meeting.mks_attended.add(mks[i])
