
# encoding: utf-8
import logging, re, difflib
from django.core.management.base import NoArgsCommand
from django.db.models import Q
from knesset.committees.models import CommitteeMeeting,ProtocolPart
from knesset.mks.models import Member
from knesset.persons.models import Person,PersonAlias

logger = logging.getLogger("open-knesset.persons.create_persons")

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):

        target_names = list(Person.objects.filter(mk__isnull=False).values_list('name',flat=True))
        names = list(Person.objects.values_list('name',flat=True))
        for n in target_names:
            matches = difflib.get_close_matches(n,names,n=30,cutoff=0.2)
            if len(matches)>1:
                for (i,m) in enumerate(matches):
                    print "%2d. %s" %(i,m[::-1])
                x = raw_input('Enter (space separated) numbers for merge father and sons. [blank=do nothing, m=give more info] ')
                if x=='m':
                    for (i,m) in enumerate(matches):
                        try:
                            p = Person.objects.get(name=m)
                            print "%2d. %s" %(i,m[::-1])
                            for r in p.roles.all():
                                print "      %s" % r.text[::-1]
                        except:
                            pass
                    x = raw_input('Enter (space separated) numbers for merge father and sons. [blank=do nothing, m=give more info] ')            
                if x and x!='m':
                    user_merge = re.findall('\d+',x)
                    if len(user_merge)>=2: 
                        merge_father = int(user_merge[0])
                        for merge_son in user_merge[1:]:
                            try:
                                Person.objects.get(name=matches[merge_father]).merge(Person.objects.get(name=matches[int(merge_son)]))
                            except:
                                print "can't find someone. probably already merged"