# encoding: utf-8
import logging, re
from django.core.management.base import NoArgsCommand

from knesset.committees.models import ProtocolPart
from knesset.mks.models import Member
from knesset.persons.models import Title,Person,Role

logger = logging.getLogger("open-knesset.persons.create_persons")



def get_name_and_role(line):
    
    delim = False
    try:
        i = re.search('(\-|–|,) '.decode('utf-8'),line, re.UNICODE).start()
        delim = True
    except AttributeError:
        i = len(line)
    try:
        i2 = re.search('(\-|–|,)\w'.decode('utf-8'),line, re.UNICODE).start()
        delim = True
    except AttributeError:
        i2 = len(line)
    
    if not delim:
        # didn't find any delimiters, ask user
        print "Didn't find any delimiters in:"
        print line[::-1]
        print line
        x = raw_input('Please enter the name+title to use (blank to use whole line as name, 0 - ignore this line) ')
        if x=='0':
            return None
        if not x:
            name = line
            role = ''
        else:
            name = x.decode('utf8')
            x = raw_input('Please enter role to use (blank to have no role) ')
            role = x.decode('utf8')
        logger.debug("user entered values: name=%s role=%s" % (name,role))
        return {'name':name, 'role':role}
    if i2<i: # non spaced delimiter is before the spaced delimiter, ask user what to do
        print "Found non spaced delimiter in"
        print line[::-1]
        pos = []
        last_pos = -1
        try:
            while True:
                last_pos = re.search('(\-|–|,)'.decode('utf-8'),line[last_pos+1:], re.UNICODE).start()+last_pos+1
                pos.append(last_pos)
        except:
            pass
        pos.append(len(line))
        line2 = ' '* (len(line)+1)
        for (n,p) in enumerate(pos):
            line2 = '%s%d%s' % (line2[:p],n,line2[p+1:])
        print line2[::-1]
        x = input('which delimiter should I use? ')
        i = pos[x]

    name = line[:i].strip()
    role = line[i+1:].strip()
    print "name = %s\nrole = %s" % (name,role)
    return {'name':name, 'role':role}

def create_names_from_attendees_part(part):
    for line in part.body.split('\n'):
        if len(line)<3:
            continue
        logger.debug("%d %s" % (part.meeting.id, line))
        x = get_name_and_role(line)
        if not x:
            continue
        name = x['name']
        role = x['role']
        
        found_titles = set()
        for t in Title.objects.all():
            i = name.find(t.name) 
            if i >= 0:
                name = (name[:i]+name[i+len(t.name):]).strip()
                found_titles.add(t)
        (p,created) = Person.objects.get_or_create(name=name)
        if created: 
            p.save()
            logger.debug("person created: %s" % p.name)
        else:
            logger.debug("person already exists: %s" % p.name)
        
        for t in found_titles:
            p.titles.add(t)
            logger.debug("adding title: %s" % t)
            
        if role:
            (r,created) = Role.objects.get_or_create(text=role,person=p)
            if created:
                r.save()
                logger.debug("created role %s" % r.text)
            else:
                logger.debug("role already exists: %s" % r.text)
    

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        if not Title.objects.count():
            logger.debug("no titles found. creating.")
            Title.objects.create(name='חה"כ')
            Title.objects.create(name='ח"כ')
            Title.objects.create(name='ד"ר')
            Title.objects.create(name="דר'")
            Title.objects.create(name='פרופסור')
            Title.objects.create(name='פרופ\'')
            Title.objects.create(name='עו"ד')
            Title.objects.create(name='רו"ח')
            # army ranks
            Title.objects.create(name='סג"מ')
            Title.objects.create(name='סגן')
            Title.objects.create(name='סרן')
            Title.objects.create(name='רס"ן')
            Title.objects.create(name='סא"ל')
            Title.objects.create(name='אל"מ')
            Title.objects.create(name='תא"ל')
            Title.objects.create(name='אלוף')
            Title.objects.create(name='רא"ל')
            # police ranks
            Title.objects.create(name='פקד')
            Title.objects.create(name='רפ"ק')
            Title.objects.create(name='סנ"צ')
            Title.objects.create(name='תנ"צ')
            Title.objects.create(name='נצ"מ')
            Title.objects.create(name='ניצב')
            #
            Title.objects.create(name='ד"גס')
            Title.objects.create(name='גנ"מ')
            
            
        t = Title.objects.get(name='חה"כ')
        for member in Member.objects.all():
            (person,created) = Person.objects.get_or_create(name=member.name)
            person.titles.add(t)
            person.mk = member
            person.save()
        a = 'מוזמנים'.decode('utf-8')
        for part in ProtocolPart.objects.filter(header=a):
            create_names_from_attendees_part(part)
            
        # Find persons in all protocol parts:    
        names = list(Person.objects.values_list('name',flat=True))
        names.sort(key=lambda x:len(x), reverse=True)
        for p in ProtocolPart.objects.filter(speaker__isnull=True):
            found = False
            for name in names:
                if p.header.find(name)>=0: 
                    p.speaker = Person.objects.get(name=name)
                    p.save()
                    found = True
            if not found:
                #print "Not found: %s" % p.header
                pass