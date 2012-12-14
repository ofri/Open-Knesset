# encoding: utf-8
import logging, re
from optparse import make_option
from django.core.management.base import NoArgsCommand
from django.db.models import Q,Max
from committees.models import ProtocolPart
from mks.models import Member
from persons.models import Person,PersonAlias,Title,Role,ProcessedProtocolPart

logger = logging.getLogger("open-knesset.persons.create_persons")

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--dont_ask', action='store_true', dest='dont_ask',
            help="always answer 'ignore' instead of asking the user. used for debugging"),
    )
    
    problematic_lines = None
    dont_ask = False
    
    def get_name_and_role(self,line):    
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
            if self.dont_ask:
                return None
            if line in self.problematic_lines: # we already asked the user about this exact line. 
                return None # no need to ask again
            self.problematic_lines.append(line) # make sure we don't ask again in the future

            print "Didn't find any delimiters in:"
            print line[::-1]
            print line
            x = raw_input('Please enter the name+title to use (blank to use whole line as name, "-" to ignore this line) ')
            if x=='-':
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
            if self.dont_ask:
                return None
            if line in self.problematic_lines: # we already asked the user about this exact line. 
                return None # no need to ask again
            self.problematic_lines.append(line) # make sure we don't ask again in the future

            print "Found non spaced delimiter in"
            print line[::-1]
            pos = []
            last_pos = -1
            try:
                while True:
                    last_pos = re.search('(\-|–|, )'.decode('utf-8'),line[last_pos+1:], re.UNICODE).start()+last_pos+1
                    pos.append(last_pos)
            except:
                pass
            pos.append(len(line))
            line2 = ' '* (len(line)+1)
            for (n,p) in enumerate(pos):
                line2 = '%s%d%s' % (line2[:p],n,line2[p+1:])
            print line2[::-1]
            x = None
            while x==None: # do not change this to "while x", because x can be be 0.
                x = raw_input('which delimiter should I use? ')
                if x == '-': return None
                try:
                    x = int(x)
                except:
                    x = None
            i = pos[x]
    
        name = line[:i].strip()
        role = line[i+1:].strip()
        print "name = %s\nrole = %s" % (name,role)
        return {'name':name, 'role':role}

    def create_names_from_attendees_part(self,part):
        for line in part.body.split('\n'):
            if len(line)<3:
                continue
            logger.debug("%d %s" % (part.meeting.id, line))
            x = self.get_name_and_role(line)
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
            if len(name)>=64:
                logger.warn('name too long: %s in part %d' % (name,part.id))
                continue
            if PersonAlias.objects.filter(name=name).count():
                p = PersonAlias.objects.filter(name=name)[0].person
            elif Person.objects.filter(name=name).count():
                p = Person.objects.filter(name=name)[0]
            else:
                p = Person.objects.create(name=name)
                                
            for t in found_titles:
                p.titles.add(t)
                logger.debug("adding title: %s" % t)
                
            if role:
                try:
                    (r,created) = Role.objects.get_or_create(text=role,person=p)
                    if created:
                        r.save()
                        logger.debug("created role %s" % r.text)
                    else:
                        logger.debug("role already exists: %s" % r.text)
                except Role.MultipleObjectsReturned,e:
                    logger.warn(e)
    
    def handle_noargs(self, **options):
        
        self.dont_ask = options.get('dont_ask', False)
        
        self.problematic_lines = []
        
        titles = ['חה"כ','ח"כ','חכ"ל','ד"ר',"דר'",'פרופסור','פרופ\'','עו"ד','רו"ח','הרב',
'סג"מ','סגן','סרן','רס"ן','סא"ל','אל"מ','תא"ל','אלוף','רא"ל',
'פקד','רפ"ק','סנ"צ','תנ"צ','נצ"מ','ניצב','סג"ד','גנ"מ']
        for title in titles:
            (t,created) = Title.objects.get_or_create(name=title)
            if created:
                t.save()
            
        t = Title.objects.get(name='חה"כ')
        for member in Member.objects.all():
            (person,created) = Person.objects.get_or_create(name=member.name)
            person.titles.add(t)
            person.mk = member
            person.save()
        
        title1 = 'מוזמנים'.decode('utf-8')
        title2 = 'חברי הוועדה'.decode('utf-8')
        
        last_cm = None
        if ProcessedProtocolPart.objects.count():
            last_protocol_part = ProcessedProtocolPart.objects.all()[0]
        else: # we didn't create a ProcessedProtocolPart yet. probably the first time we're running this
            last_protocol_part = ProcessedProtocolPart.objects.create(protocol_part_id=0)
        qs = ProtocolPart.objects.filter(Q(header=title1)|Q(header=title2), id__gt=last_protocol_part.protocol_part_id)
        max_updated = 0
        for part in qs:
            if part.meeting != last_cm:
                x = raw_input("Quit? ")
                if x=='y' or x=='Y':
                    break
                print "\nCommitteeMeeting: %d" % part.meeting.id
                last_cm = part.meeting
            self.create_names_from_attendees_part(part)
            max_updated = max(max_updated,part.id)
        if max_updated:
            last_protocol_part.protocol_part_id = max_updated
            last_protocol_part.save()
