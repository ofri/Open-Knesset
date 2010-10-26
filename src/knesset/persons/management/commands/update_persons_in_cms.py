# encoding: utf-8
import logging, re
from django.core.management.base import NoArgsCommand
from django.db.models import Q
from knesset.committees.models import ProtocolPart
from knesset.mks.models import Member
from knesset.persons.models import Person,PersonAlias

logger = logging.getLogger("open-knesset.persons.create_persons")

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):

        # Find persons in all protocol parts:
        p = Person.objects.all()
        names_and_aliases = zip([x.name for x in p],p)
        p = PersonAlias.objects.all()
        names_and_aliases.extend(zip([x.name for x in p],p.person))
        names_and_aliases.sort(key=lambda x:len(x[0]), reverse=True)
        for pp_header in ProtocolPart.objects.filter(speaker__isnull=True).exclude(header='').values_list('header',flat=True):                
            for (name,person) in names_and_aliases:
                if pp_header.find(name)>=0:
                    parts_updated = ProtocolPart.objects.filter(header=pp_header).update(speaker=person)
                    print "updated speaker for %d parts to %s" % (parts_updated,person.name)
                    break
