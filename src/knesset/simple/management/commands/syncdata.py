 # This Python file uses the following encoding: utf-8
import os,sys,traceback
from django.core.management.base import NoArgsCommand
from optparse import make_option
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

import urllib2,urllib
import cookielib
import re
import gzip
import simplejson
import datetime
import time
import logging
from cStringIO import StringIO
from pyth.plugins.rtf15.reader import Rtf15Reader

from knesset.mks.models import *
from knesset.laws.models import *
from knesset.links.models import *
from knesset.committees.models import *

from django.db import connection
from django.db.models import Max,Count

import mk_info_html_parser as mk_parser

ENCODING = 'utf8'

DATA_ROOT = getattr(settings, 'DATA_ROOT',
                    os.path.join(settings.PROJECT_ROOT, 'data'))

logger = logging.getLogger("open-knesset.syncdata")

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--all', action='store_true', dest='all',
            help="runs all the syncdata sub processes (like --download --load --process --dump)"),
        make_option('--download', action='store_true', dest='download',
            help="download data from knesset website to local files."),
        make_option('--load', action='store_true', dest='load',
            help="load the data from local files to the db."),
        make_option('--process', action='store_true', dest='process',
            help="run post loading process."),
        make_option('--dump', action='store_true', dest='dump-to-file',
            help="write votes to tsv files (mainly for debug, or for research team)."),
        make_option('--update', action='store_true', dest='update',
            help="online update of votes data."),
        
    )
    help = "Downloads data from sources, parses it and loads it to the Django DB."

    requires_model_validation = False

    last_downloaded_vote_id = 0
    last_downloaded_member_id = 0

    def read_laws_page(self,index):
        url = 'http://www.knesset.gov.il/privatelaw/plaw_display.asp?LawTp=2'
        data = urllib.urlencode({'RowStart':index})
        urlData = urllib2.urlopen(url,data)
        page = urlData.read().decode('windows-1255').encode('utf-8')
        return page

    def parse_laws_page(self,page):
        names = []
        exps = []
        links = []
        count = -1
        lines = page.split('\n')
        for line in lines:
            #print line
            r = re.search("""Href=\"(.*?)\">""",line)
            if r != None:
                link = 'http://www.knesset.gov.il/privatelaw/' + r.group(1)
            r = re.search("""<td class="LawText1">(.*)""",line)
            if r != None:
                name = r.group(1).replace("</td>","").strip()
                if len(name)>1 and name.find('span')<0:
                    names.append(name)
                    links.append(link)
                    exps.append('')
                    count += 1
            if re.search("""arrResume\[\d*\]""",line) != None:
                r = re.search("""\"(.*)\"""",line)
                if r != None:
                    try:
                        exps[count] += r.group(1).replace('\t',' ')
                    except: 
                        pass

        return (names,exps,links)

    def get_laws_data(self):
        f = gzip.open(os.path.join(DATA_ROOT, 'laws.tsv.gz'), "wb")
        for x in range(0,910,26): # TODO: find limits of download
        #for x in range(0,50,26): # for debug
            page = self.read_laws_page(x)
            (names,exps,links) = self.parse_laws_page(page)
            for (name,exp,link) in zip(names,exps,links):
                f.write("%s\t%s\t%s\n" % (name,exp,link))
        f.close()

    def download_laws(self):
        """ returns an array of laws data: laws[i][0] - name, laws[i][1] - name for search, laws[i][2] - summary, laws[i][3] - link """
        laws = []
        for x in range(0,79,26): # read 4 last laws pages
            page = self.read_laws_page(x) 
            (names,exps,links) = self.parse_laws_page(page)
            for (name,exp,link) in zip(names,exps,links):
                name_for_search = self.get_search_string(name)
                laws.append((name,name_for_search,exp,link))
        return laws 

    def update_laws_data(self):
        logger.info("update laws data")
        laws = self.download_laws()
        logger.debug("finished downloading laws data")
        votes = Vote.objects.all().order_by('-time')[:200]
        for v in votes:
            search_name = self.get_search_string(v.title.encode('UTF-8'))
            for l in laws:
                if search_name.find(l[1]) >= 0:
                    #print "match"
                    v.summary = l[2]
                    v.save()
                    try:
                        (link, created) = Link.objects.get_or_create(title=u'מסמך הצעת החוק באתר הכנסת', url=l[3], content_type=ContentType.objects.get_for_model(v), object_pk=str(v.id))
                        if created:                         
                            link.save()
                    except Exception, e:
                        logger.error(e)

            if v.full_text == None:
                self.get_full_text(v)
        logger.debug("finished updating laws data")


    def update_votes(self):
        """This function updates votes data online, without saving to files."""        
        
        logger.info("update votes")        
        current_max_src_id = Vote.objects.aggregate(Max('src_id'))['src_id__max']
        if current_max_src_id == None: # the db contains no votes, meaning its empty
            print "DB is empty. --update can only be used to update, not for first time loading. \ntry --all, or get some data using initial_data.json\n"
            return
        vote_id = current_max_src_id+1 # first vote to look for is the max_src_id we have plus 1
        limit_src_id = vote_id + 20 # look for next 20 votes. if results are found, this value will be incremented. 
        while vote_id < limit_src_id:        
            (page, vote_src_url) = self.read_votes_page(vote_id)
            title = self.get_page_title(page)
            if(title == """הצבעות במליאה-חיפוש"""): # found no vote with this id                
                logger.debug("no vote found at id %d" % vote_id)
            else:
                limit_src_id = vote_id + 20 # results found, so we'll look for at least 20 more votes
                (vote_label, vote_meeting_num, vote_num, date) = self.get_vote_data(page)
                
        #(vote_id, vote_src_url, vote_label, vote_meeting_num, vote_num, vote_time_string, count_for, count_against, count_abstain, count_no_vote) = line.split('\t') 
        #f2.write("%d\t%s\t%s\t%s\t%s\t%s\t%d\t%d\t%d\t%d\n" % (id, src_url, name, meeting_num, vote_num, date))
                logger.debug("downloaded data with vote id %d" % vote_id)
                vote_time_string = date.replace('&nbsp;',' ')
                for i in self.heb_months:
                    if i in vote_time_string:
                        month = self.heb_months.index(i)+1
                day = re.search("""(\d\d?)""", vote_time_string).group(1)
                year = re.search("""(\d\d\d\d)""", vote_time_string).group(1)
                vote_hm = datetime.datetime.strptime ( vote_time_string.split(' ')[-1], "%H:%M" )
                vote_date = datetime.date(int(year),int(month),int(day))
                vote_time = datetime.datetime(int(year), int(month), int(day), vote_hm.hour, vote_hm.minute)
                #vote_label_for_search = self.get_search_string(vote_label)

                try:
                    v = Vote.objects.get(src_id=vote_id)                
                    created = False
                except:
                    v = Vote(title=vote_label, time_string=vote_time_string, importance=1, src_id=vote_id, time=vote_time)
                    try:
                        vote_meeting_num = int(vote_meeting_num)
                        v.meeting_number = vote_meeting_num
                    except:
                        pass
                    try:
                        vote_num = int(vote_num)
                        v.vote_number = vote_num
                    except:
                        pass
                    v.src_url = vote_src_url
                    v.save()
                    if v.full_text_url != None:
                        l = Link(title=u'מסמך הצעת החוק באתר הכנסת', url=v.full_text_url, content_type=ContentType.objects.get_for_model(v), object_pk=str(v.id))
                        l.save()

                results = self.read_member_votes(page, return_ids=True)
                for (voter_id,voter_party,vote) in results:
                    #f.write("%d\t%s\t%s\t%s\n" % (id,voter,party,vote))                    

                    # transform party names to canonical form
                    if(voter_party in self.party_aliases):
                        voter_party = self.party_aliases[voter_party]

                    p = Party.objects.get(name=voter_party)
                                    
                    # get the member voting                
                    try:
                        m = Member.objects.get(pk=int(voter_id))
                    except:
                        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                        logger.error("%svoter_id = %s", ''.join(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback), str(voter_id)))
                        
                    # add the current member's vote
                    va,created = VoteAction.objects.get_or_create(vote = v, member = m, type = vote)
                    if created:
                        va.save()

                
                update_vote_properties(v)
                v = Vote.objects.get(src_id=vote_id)
                self.find_synced_protocol(v)
                self.get_full_text(v)

            vote_id += 1 

    def get_votes_data(self):
        self.update_last_downloaded_vote_id()
        f  = gzip.open(os.path.join(DATA_ROOT, 'results.tsv.gz'), "ab")
        f2 = gzip.open(os.path.join(DATA_ROOT, 'votes.tsv.gz'),"ab")
        r = range(self.last_downloaded_vote_id+1,13400) # this is the range of page ids to go over. currently its set manually.
        for id in r:
            (page, src_url) = self.read_votes_page(id)
            title = self.get_page_title(page)
            if(title == """הצבעות במליאה-חיפוש"""): # found no vote with this id
                logger.debug("no vote found at id %d" % id)
            else:
                count_for = 0
                count_against = 0
                count_abstain = 0
                count_no_vote = 0
                (name, meeting_num, vote_num, date) = self.get_vote_data(page)
                results = self.read_member_votes(page)
                for (voter,party,vote) in results:
                    f.write("%d\t%s\t%s\t%s\n" % (id,voter,party,vote))
                    if(vote=="for"):
                        count_for += 1
                    if(vote=="against"):
                        count_against += 1
                    if(vote=="abstain"):
                        count_abstain += 1
                    if(vote=="no-vote"):
                        count_no_vote += 1
                f2.write("%d\t%s\t%s\t%s\t%s\t%s\t%d\t%d\t%d\t%d\n" % (id, src_url, name, meeting_num, vote_num, date, count_for, count_against, count_abstain, count_no_vote))
                logger.debug("downloaded data with vote id %d" % id)
            #print " %.2f%% done" % ( (100.0*(float(id)-r[0]))/(r[-1]-r[0]) )
        f.close()
        f2.close()        

    def update_last_downloaded_member_id(self):
        """
        Reads local members file, and sets self.last_downloaded_member_id to the highest id found in the file.
        This is later used to skip downloading of data alreay downloaded.
        """
        try:
            f = gzip.open(os.path.join(DATA_ROOT, 'members.tsv.gz'))
        except:
            self.last_downloaded_member_id = 0
            logger.debug("members file does not exist. setting last_downloaded_member_id to 0")
            return            
        content = f.read().split('\n')
        for line in content:
            if(len(line)<2):
                continue
            s = line.split('\t')
            id = int(s[0])
            if id > self.last_downloaded_member_id:
                self.last_downloaded_member_id = id
        logger.debug("last member id found in local files is %d. " % self.last_downloaded_member_id)
        f.close()
    
    def get_members_data(self):
        """downloads members data to local files
        """
        self.update_last_downloaded_member_id()

        f  = gzip.open(os.path.join(DATA_ROOT, 'members.tsv.gz'), "ab")

        fields = ['img_link','טלפון','פקס','אתר נוסף','דואר אלקטרוני','מצב משפחתי','מספר ילדים','תאריך לידה','שנת לידה','מקום לידה','תאריך פטירה','שנת עלייה'] 
        # note that hebrew strings order is right-to-left
        # so output file order is id, name, img_link, phone, ...

        fields = [unicode(field.decode('utf8')) for field in fields]

        for id in range(self.last_downloaded_member_id+1,900): # TODO - find max member id in knesset website and use here
            m = mk_parser.MKHtmlParser(id).Dict
            if (m.has_key('name') and m['name'] != None): name = m['name'].encode(ENCODING).replace('&nbsp;',' ').replace(u'\xa0',' ')
            else: continue
            f.write("%d\t%s\t" % (  id, name ))
            for field in fields:
                value = ''
                if (m.has_key(field) and m[field]!=None): 
                    value = m[field].encode(ENCODING)
                f.write("%s\t" % (  value ))
            f.write("\n")
            
        f.close()

    def download_all(self):
        self.get_members_data()        
        self.get_votes_data()
        self.get_laws_data()


    def update_last_downloaded_vote_id(self):
        """
        Reads local votes file, and sets self.last_downloaded_id to the highest id found in the file.
        This is later used to skip downloading of data alreay downloaded.
        """
        try:
            f = gzip.open(os.path.join(DATA_ROOT, 'votes.tsv.gz'))
        except:
            self.last_downloaded_vote_id = 0
            logger.debug("votes file does not exist. setting last_downloaded_vote_id to 0")
            return            
        content = f.read().split('\n')
        for line in content:
            if(len(line)<2):
                continue
            s = line.split('\t')
            vote_id = int(s[0])
            if vote_id > self.last_downloaded_vote_id:
                self.last_downloaded_vote_id = vote_id
        logger.debug("last id found in local files is %d. " % self.last_downloaded_vote_id)
        f.close()


    def update_members_from_file(self):
        f = gzip.open(os.path.join(DATA_ROOT, 'members.tsv.gz'))
        content = f.read().split('\n')
        for line in content:
            if len(line) <= 1:
                continue
            (member_id, name, img_url, phone, fax, website, email, family_status, number_of_children, 
             date_of_birth, year_of_birth, place_of_birth, date_of_death, year_of_aliyah, extra) = line.split('\t') 
            if email != '':
                email = email.split(':')[1]
            try:
                if date_of_birth.find(',')>=0:
                    date_of_birth = date_of_birth.split(',')[1].strip(' ')
                date_of_birth = datetime.datetime.strptime ( date_of_birth, "%d/%m/%Y" )
            except:
                date_of_birth = None
            try:
                if date_of_birth.find(',')>=0:
                    date_of_death = date_of_birth.split(',')[1].strip(' ')
                date_of_death = datetime.datetime.strptime ( date_of_death, "%d/%m/%Y" )
            except:
                date_of_death = None
            try: year_of_birth = int(year_of_birth)
            except: year_of_birth = None
            try: year_of_aliyah = int(year_of_aliyah)
            except: year_of_aliyah = None
            try: number_of_children = int(number_of_children)
            except: number_of_children = None

            try:
                m = Member.objects.get(id=member_id)
            except: # member_id not found. create new
                m = Member(id=member_id, name=name, img_url=img_url, phone=phone, fax=fax, website=None, email=email, family_status=family_status, 
                            number_of_children=number_of_children, date_of_birth=date_of_birth, place_of_birth=place_of_birth, 
                            date_of_death=date_of_death, year_of_aliyah=year_of_aliyah)
                m.save()
                if len(website)>0:
                    l = Link(title='אתר האינטרנט של %s' % name, url=website, content_type=ContentType.objects.get_for_model(m), object_pk=str(m.id))
                    l.save()


    def get_search_string(self,s):
        s = s.replace('\xe2\x80\x9d','').replace('\xe2\x80\x93','')
        return re.sub(r'["\(\) ,-]', '', s)

    heb_months = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר']


    # some party names appear in the knesset website in several forms.
    # this dictionary is used to transform them to canonical form.
    party_aliases = {'עבודה':'העבודה',
                    'ליכוד':'הליכוד',
                    'ש"ס-התאחדות ספרדים שומרי תורה':'ש"ס',
                    'יחד (ישראל חברתית דמוקרטית) והבחירה הדמוקרטית':'יחד (ישראל חברתית דמוקרטית) והבחירה הדמוקרטית',
                    'בל"ד-ברית לאומית דמוקרטית':'בל"ד',
                    'אחריות לאומית':'קדימה',
                    'יחד (ישראל חברתית דמוקרטית) והבחירה הדמוקרטית':'מרצ-יחד והבחירה הדמוקרטית',
                    'יחד והבחירה הדמוקרטית':'מרצ-יחד והבחירה הדמוקרטית',
                    'יחד והבחירה הדמוקרטית (מרצ לשעבר)':'מרצ-יחד והבחירה הדמוקרטית',
                    'יחד (ישראל חברתית דמוקרטית) והבחירה הדמוקרטית':'מרצ-יחד והבחירה הדמוקרטית',
                    'יחד  (ישראל חברתית דמוקרטית) והבחירה הדמוקרטית':'מרצ-יחד והבחירה הדמוקרטית',
                    }


    def update_db_from_files(self):
        logger.debug("Update DB From Files")

        try:
            laws = [] # of lists: [name,name_for_search,explanation,link]
            f = gzip.open(os.path.join(DATA_ROOT, 'laws.tsv.gz'))
            content = f.read().split('\n')
            for line in content:
                law = line.split('\t')
                if len(law)==3:
                    name_for_search = self.get_search_string(law[0])
                    law.insert(1, name_for_search)
                    laws.append(law)
            f.close()

            parties = dict() # key: party-name; value: Party
            members = dict() # key: member-name; value: Member
            votes   = dict() # key: id; value: Vote
            memberships = dict() # key: (member.id,party.id)
            current_vote = None # used to track what vote we are on, to create vote objects only for new votes
            current_max_src_id = Vote.objects.aggregate(Max('src_id'))['src_id__max']
            if current_max_src_id == None: # the db contains no votes, meanins its empty
                current_max_src_id = 0

            logger.debug("processing votes data")
            f = gzip.open(os.path.join(DATA_ROOT, 'votes.tsv.gz'))
            content = f.read().split('\n')
            for line in content:
                if len(line) <= 1:
                    continue
                (vote_id, vote_src_url, vote_label, vote_meeting_num, vote_num, vote_time_string, count_for, count_against, count_abstain, count_no_vote) = line.split('\t') 
                #if vote_id < current_max_src_id: # skip votes already parsed.
                #    continue  
                vote_time_string = vote_time_string.replace('&nbsp;',' ')
                for i in self.heb_months:
                    if i in vote_time_string:
                        month = self.heb_months.index(i)+1
                day = re.search("""(\d\d?)""", vote_time_string).group(1)
                year = re.search("""(\d\d\d\d)""", vote_time_string).group(1)
                vote_hm = datetime.datetime.strptime ( vote_time_string.split(' ')[-1], "%H:%M" )
                vote_date = datetime.date(int(year),int(month),int(day))
                vote_time = datetime.datetime(int(year), int(month), int(day), vote_hm.hour, vote_hm.minute)
                vote_label_for_search = self.get_search_string(vote_label)

                if vote_date < datetime.date(2009, 02, 24): # vote before 18th knesset
                    continue

                try:
                    v = Vote.objects.get(src_id=vote_id)                
                    created = False
                except:
                    v = Vote(title=vote_label, time_string=vote_time_string, importance=1, src_id=vote_id, time=vote_time)
                    try:
                        vote_meeting_num = int(vote_meeting_num)
                        v.meeting_number = vote_meeting_num
                    except:
                        pass
                    try:
                        vote_num = int(vote_num)
                        v.vote_number = vote_num
                    except:
                        pass
                    v.src_url = vote_src_url
                    for law in laws:
                        (law_name,law_name_for_search,law_exp,law_link) = law
                        if vote_label_for_search.find(law_name_for_search) >= 0:
                            v.summary = law_exp
                            v.full_text_url = law_link                    
                    v.save()
                    if v.full_text_url != None:
                        l = Link(title=u'מסמך הצעת החוק באתר הכנסת', url=v.full_text_url, content_type=ContentType.objects.get_for_model(v), object_pk=str(v.id))
                        l.save()
                votes[int(vote_id)] = v
            f.close()

            logger.debug("processing member votes data")
            f = gzip.open(os.path.join(DATA_ROOT, 'results.tsv.gz'))
            content = f.read().split('\n')
            for line in content:
                if(len(line)<2):
                    continue
                s = line.split('\t') # (id,voter,party,vote)
                
                vote_id = int(s[0])
                voter = s[1]
                voter_party = s[2]

                # transform party names to canonical form
                if(voter_party in self.party_aliases):
                    voter_party = self.party_aliases[voter_party]

                vote = s[3]

                try:
                    v = votes[vote_id]
                except KeyError: #this vote was skipped in this read, also skip voteactions and members
                    continue 
                vote_date = v.time.date()

                # create/get the party appearing in this vote 
                if voter_party in parties:
                    p = parties[voter_party]
                    created = False
                else:
                    p,created = Party.objects.get_or_create(name=voter_party)
                    parties[voter_party] = p
                #if created: # this is magic needed because of unicode chars. if you don't do this, the object p will have gibrish as its name. 
                            #only when it comes back from the db it has valid unicode chars.
                #    p = Party.objects.get(name=voter_party) 
                
                # use this vote's time to update the party's start date and end date
                if (p.start_date is None) or (p.start_date > vote_date):
                    p.start_date = vote_date
                if (p.end_date is None) or (p.end_date < vote_date):
                    p.end_date = vote_date
                if created: # save on first time, so it would have an id, be able to link, etc. all other updates are saved in the end
                    p.save() 
                
                # create/get the member voting
                if voter in members:
                    m = members[voter]
                    created = False
                else:
                    try:
                        m = Member.objects.get(name=voter)
                    except:   # if there are several people with same age, 
                        m = Member.objects.filter(name=voter).order_by('-date_of_birth')[0] # choose the younger. TODO: fix this
                    members[voter] = m
                #m.party = p;
                #if created: # again, unicode magic
                #    m = Member.objects.get(name=voter)
                # use this vote's date to update the member's dates.
                if (m.start_date is None) or (m.start_date > vote_date):
                    m.start_date = vote_date
                if (m.end_date is None) or (m.end_date < vote_date):
                    m.end_date = vote_date
                #if created: # save on first time, so it would have an id, be able to link, etc. all other updates are saved in the end
                #    m.save()
        
                    
                # create/get the membership (connection between member and party)
                if ((m.id,p.id) in memberships):
                    ms = memberships[(m.id,p.id)]                
                    created = False
                else:
                    ms,created = Membership.objects.get_or_create(member=m,party=p)
                    memberships[(m.id,p.id)] = ms
                #if created: # again, unicode magic
                #    ms = Membership.objects.get(member=m,party=p)
                # again, update the dates on the membership
                if (ms.start_date is None) or (ms.start_date > vote_date):
                    ms.start_date = vote_date
                if (ms.end_date is None) or (ms.end_date < vote_date):
                    ms.end_date = vote_date
                if created: # save on first time, so it would have an id, be able to link, etc. all other updates are saved in the end
                    ms.save()    
                    
                # add the current member's vote
                
                va,created = VoteAction.objects.get_or_create(vote = v, member = m, type = vote)
                if created:
                    va.save()
                
            logger.debug("done")
            logger.debug("saving data: %d parties, %d members, %d memberships " % (len(parties), len(members), len(memberships) ))
            for p in parties:
                parties[p].save()
            for m in members:
                members[m].save()
            Member.objects.filter(end_date__isnull=True).delete() # remove members that haven't voted at all - no end date
            for ms in memberships:
                memberships[ms].save()
            #for va in voteactions:
            #    voteactions[va].save()
            logger.debug("done")
            f.close()
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            logger.error("%s", ''.join(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)))
            

    def calculate_votes_importances(self):
        """
        Calculates votes importances. currently uses rule of thumb: number of voters against + number of voters for / 120.
        """    
        for v in Vote.objects.all():
            v.importance = float(v.votes.filter(voteaction__type='for').count() + v.votes.filter(voteaction__type='against').count()) / 120
            v.save()
        
    def calculate_correlations(self):
        """
        Calculates member pairs correlation on votes.
        """
        # TODO: refactor the hell out of this one...
        return 
        print "Calculate Correlations"
        try:     
            cursor = connection.cursor()
            print "%s truncate correlations table" % str(datetime.datetime.now())
            Correlation.objects.all().delete()
            print "%s calculate correlations"  % str(datetime.datetime.now())
            cursor.execute("""insert into mks_correlation (m1_id,m2_id,score) (
                select m1 as m1_id, m2 as m2_id,sum(score) as score from (
                select a1.member_id as m1,a2.member_id as m2, count(*) as score from (
                (select * from laws_votes where type='for') a1,
                (select * from laws_votes where type='for') a2
                ) where a1.vote_id = a2.vote_id and a1.member_id < a2.member_id group by a1.member_id,a2.member_id
                union
                select a1.member_id as m1,a2.member_id as m2, count(*) as score from (
                (select * from laws_votes where type='against') a1,
                (select * from laws_votes where type='against') a2
                ) where a1.vote_id = a2.vote_id and a1.member_id < a2.member_id group by a1.member_id,a2.member_id
                union
                select a1.member_id as m1,a2.member_id as m2, -count(*) as score from (
                (select * from laws_votes where type='for') a1,
                (select * from laws_votes where type='against') a2
                ) where a1.vote_id = a2.vote_id and a1.member_id < a2.member_id group by a1.member_id,a2.member_id
                union
                select a1.member_id as m1,a2.member_id as m2, -count(*) as score from (
                (select * from laws_votes where type='against') a1,
                (select * from laws_votes where type='for') a2
                ) where a1.vote_id = a2.vote_id and a1.member_id < a2.member_id group by a1.member_id,a2.member_id
                
                ) a group by m1,m2
                )""".replace('\n',''))
            print "%s done"  % str(datetime.datetime.now())
            print "%s normalizing correlation"  % str(datetime.datetime.now())
            cursor.execute("""update mks_correlation,
                (select member_id,sum(vote_count) as vote_count from (
                select member_id,count(*) as vote_count from laws_votes where type='for' group by member_id
                union
                select member_id,count(*) as vote_count from laws_votes where type='against' group by member_id
                ) a 
                group by member_id) a1,
                (select member_id,sum(vote_count) as vote_count from (
                select member_id,count(*) as vote_count from laws_votes where type='for' group by member_id
                union
                select member_id,count(*) as vote_count from laws_votes where type='against' group by member_id
                ) a 
                group by member_id) a2
                set mks_correlation.normalized_score = mks_correlation.score / sqrt(a1.vote_count) / sqrt(a2.vote_count)*100 
                where mks_correlation.m1_id = a1.member_id and mks_correlation.m2_id = a2.member_id""")

        except Exception,e:
            print "error: %s" % e
     

    def read_votes_page(self,voteId, retry=0):
        """
        Gets a votes page from the knesset website.
        returns a string (utf encoded)
        """
        url = "http://www.knesset.gov.il/vote/heb/Vote_Res_Map.asp?vote_id_t=%d" % voteId
        try:        
            urlData = urllib2.urlopen(url)
            page = urlData.read().decode('windows-1255').encode('utf-8')
            time.sleep(2)
        except Exception,e:
            logger.warn(e)
            if retry < 5:
                logger.warn("waiting some time and trying again... (# of retries = %d)" % retry+1)
                page = read_votes_page(self,voteId, retry+1)
            else:
                logger.error("failed too many times. last error: %s", e)
                return None
        return (page, url)

    def read_member_votes(self,page,return_ids=False):
        """
        Returns a tuple of (name, party, vote) describing the vote found in page, where:
         name is a member name
         party is the member's party
         vote is 'for','against','abstain' or 'no-vote'
         if return_ids = True, it will return member id, and not name as first element.
        """
        results = []
        pattern = re.compile("""Vote_Bord""")
        match = pattern.split(page)
        for i in match:
            vote = ""
            if(re.match("""_R1""", i)):
                vote = "for"
            if(re.match("""_R2""", i)):
                vote = "against"
            if(re.match("""_R3""", i)):
                vote = "abstain"
            if(re.match("""_R4""", i)):
                vote = "no-vote"
            if(vote != ""):
                name = re.search("""DataText4>([^<]*)</a>""",i).group(1);
                name = re.sub("""&nbsp;""", " ", name)
                m_id = re.search("""mk_individual_id_t=(\d+)""",i).group(1)
                party = re.search("""DataText4>([^<]*)</td>""",i).group(1);
                party = re.sub("""&nbsp;""", " ", party)
                if(party == """ " """):
                    party = last_party
                else:
                    last_party = party 
                if return_ids:
                    results.append((m_id, party, vote))  
                else:
                    results.append((name, party, vote))  

        return results


    def get_page_title(self,page):
        """
        Returns the title of a vote page
        """
        title = re.search("""<TITLE>([^<]*)</TITLE>""", page)
        return title.group(1)

    def get_vote_data(self,page):
        """
        Returns name, meeting number, vote number and date from a vote page
        """
        meeting_num = re.search("""מספר ישיבה: </td>[^<]*<[^>]*>([^<]*)<""", page).group(1)
        vote_num = re.search("""מספר הצבעה: </td>[^<]*<[^>]*>([^<]*)<""", page).group(1)
        name = re.search("""שם החוק: </td>[^<]*<[^>]*>([^<]*)<""", page).group(1)
        name = name.replace("\t"," ")
        name = name.replace("\n"," ")
        name = name.replace("\r"," ")
        name = name.replace("&nbsp;"," ")
        date = re.search("""תאריך: </td>[^<]*<[^>]*>([^<]*)<""",page).group(1)
        return (name, meeting_num, vote_num, date)

    def find_pdf(self,vote_title):
        """
        Gets a vote title, and searches google for relevant files about it.
        NOT FINISHED, AND CURRENTLY NOT USED.
        """
        r = ''
        try:        
            q = vote_title.replace('-',' ').replace('"','').replace("'","").replace("`","").replace(",","").replace('(',' ').replace(')',' ').replace('  ',' ').replace(' ','+')
            q = q.replace('אישור החוק','')
            q = q+'+pdf'
            q = urllib2.quote(q)
            url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s" % q
            r = simplejson.loads(urllib2.urlopen(url).read().decode('utf-8'))['responseData']['results']
        except Exception,e:
            print "error: %s" % e
            return ''
        if len(r) > 0:
            print "full_text_url for vote %s : %s" % (q,r[0]['url'].encode('utf-8'))
            return r[0]['url']
        else:
            #print "didn't find a full_text_url for vote %s , q = %s" % (vote_title,q)
            return ''

    def find_synced_protocol(self, v):
        try:
            search_text = ''
            url = "http://online.knesset.gov.il/eprotocol/PUBLIC/SearchPEOnline.aspx"
            to_day = from_day = str(v.time.day)
            to_month = from_month = str(v.time.month)
            to_year = from_year = str(v.time.year)
            m = re.search(' - (.*),', v.title)
            if not m:
                logger.debug("couldn't create search string for vote\nvote.id=%s\nvote.title=%s\n", str(v.id), v.title)
                return    
            search_text = urllib2.quote(m.group(1).replace('(','').replace(')','').replace('`','').encode('utf8'))

            # I'm really sorry for the next line, but I really had no choice:
            params = '__EVENTARGUMENT=&__EVENTTARGET=&__LASTFOCUS=&__PREVIOUSPAGE=bEfxzzDx0cPgMul_87gMIa3L4OOi0E21r4EnHaLHKQAsWXdde-10pzxRGZZaJFCK0&__SCROLLPOSITIONX=0&__SCROLLPOSITIONY=0&__VIEWSTATE=%2FwEPDwUKMjA3MTAzNTc1NA8WCB4VU0VTU0lPTl9SQU5ET01fTlVNQkVSAswEHhFPTkxZX0RBVEVTX1NFQVJDSGgeEFBSRVZJRVdfRFRfQ0FDSEUy5AQAAQAAAP%2F%2F%2F%2F8BAAAAAAAAAAQBAAAA7AFTeXN0ZW0uQ29sbGVjdGlvbnMuR2VuZXJpYy5EaWN0aW9uYXJ5YDJbW1N5c3RlbS5JbnQzMiwgbXNjb3JsaWIsIFZlcnNpb249Mi4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5XSxbU3lzdGVtLkRhdGEuRGF0YVRhYmxlLCBTeXN0ZW0uRGF0YSwgVmVyc2lvbj0yLjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODldXQMAAAAHVmVyc2lvbghDb21wYXJlcghIYXNoU2l6ZQADAAiRAVN5c3RlbS5Db2xsZWN0aW9ucy5HZW5lcmljLkdlbmVyaWNFcXVhbGl0eUNvbXBhcmVyYDFbW1N5c3RlbS5JbnQzMiwgbXNjb3JsaWIsIFZlcnNpb249Mi4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5XV0IAAAAAAkCAAAAAAAAAAQCAAAAkQFTeXN0ZW0uQ29sbGVjdGlvbnMuR2VuZXJpYy5HZW5lcmljRXF1YWxpdHlDb21wYXJlcmAxW1tTeXN0ZW0uSW50MzIsIG1zY29ybGliLCBWZXJzaW9uPTIuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OV1dAAAAAAseFEFQUFJOQ19DT1VOVEVSX0NBQ0hFMtgEAAEAAAD%2F%2F%2F%2F%2FAQAAAAAAAAAEAQAAAOABU3lzdGVtLkNvbGxlY3Rpb25zLkdlbmVyaWMuRGljdGlvbmFyeWAyW1tTeXN0ZW0uSW50MzIsIG1zY29ybGliLCBWZXJzaW9uPTIuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OV0sW1N5c3RlbS5JbnQzMiwgbXNjb3JsaWIsIFZlcnNpb249Mi4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5XV0DAAAAB1ZlcnNpb24IQ29tcGFyZXIISGFzaFNpemUAAwAIkQFTeXN0ZW0uQ29sbGVjdGlvbnMuR2VuZXJpYy5HZW5lcmljRXF1YWxpdHlDb21wYXJlcmAxW1tTeXN0ZW0uSW50MzIsIG1zY29ybGliLCBWZXJzaW9uPTIuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OV1dCAAAAAAJAgAAAAAAAAAEAgAAAJEBU3lzdGVtLkNvbGxlY3Rpb25zLkdlbmVyaWMuR2VuZXJpY0VxdWFsaXR5Q29tcGFyZXJgMVtbU3lzdGVtLkludDMyLCBtc2NvcmxpYiwgVmVyc2lvbj0yLjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODldXQAAAAALFgJmD2QWAgIDD2QWAgIDD2QWCgIDDw8WAh4EVGV4dAX%2BBiBTRUxFQ1QgICAgIHRNZXRhRGF0YS5pSXRlbUlELCB0TWV0YURhdGEuaVRvcklELCB0TWV0YURhdGEuaUl0ZW1UeXBlLCB0TWV0YURhdGEuaVBhcmVudCwgdE1ldGFEYXRhLmlJdGVtUmF3SWQsIHRNZXRhRGF0YS5zVGl0bGUsICAgICAgICAgICAgICB0TWV0YURhdGEuc1RleHQsIHRNZXRhRGF0YS5pUGFnZSwgIHRNZXRhRGF0YS5pV29yZENvdW50ZXIsIHRNZXRhRGF0YS5pQnVsa051bSwgdE1ldGFEYXRhLmlFbGVtZW50SW5lZHhlciAgRlJPTSAgICAgICB0RGlzY3Vzc2lvbnMgSU5ORVIgSk9JTiAgICAgICAgICAgICB0VG9yaW0gT04gdERpc2N1c3Npb25zLmlEaXNjSUQgPSB0VG9yaW0uaURpc2NJRCBJTk5FUiBKT0lOICAgICAgICAgICAgIHRNZXRhRGF0YSBPTiB0VG9yaW0uaVRvciA9IHRNZXRhRGF0YS5pVG9ySUQgIFdIRVJFICB0VG9yaW0uYkhhc0ZpbmFsRG9jPTAgQU5EICAoQ09OVEFJTlMoc1RleHQsIE4nIteQ15nXqdeV16gg15TXl9eV16cg15TXptei16og15fXldenINeT15XXkyDXkdefINeS15XXqNeZ15XXnyDXqteZ16fXldefINeU16rXqSIi16IgMjAxMCIgICcpIE9SIENPTlRBSU5TKHNUaXRsZSwgTici15DXmdep15XXqCDXlNeX15XXpyDXlNem16LXqiDXl9eV16cg15PXldeTINeR158g15LXldeo15nXldefINeq15nXp9eV158g15TXqtepIiLXoiAyMDEwIiAgJykpIEFORCAgREFURURJRkYoREFZLCAnMi8yMi8yMDEwJyAsIHREaXNjdXNzaW9ucy5kRGF0ZSk%2BPTAgQU5EICBEQVRFRElGRihEQVksIHREaXNjdXNzaW9ucy5kRGF0ZSwgJzIvMjIvMjAxMCcpPj0wIEFORCAgdERpc2N1c3Npb25zLmlLbmVzc2V0IElOICgxOCkgQU5EICB0RGlzY3Vzc2lvbnMuaURpc2NUeXBlID0gMSBPUkRFUiBCWSBbaVRvcklEXSBERVNDLCBbaUVsZW1lbnRJbmVkeGVyXWRkAgUPDxYCHwRlZGQCBw9kFhYCAQ8PFgIfBAUi15fXmdek15XXqSDXkSLXk9eR16jXmSDXlNeb16DXodeqImRkAgMPD2QWAh4Jb25rZXlkb3duBcgBaWYgKChldmVudC53aGljaCAmJiBldmVudC53aGljaCA9PSAxMykgfHwgKGV2ZW50LmtleUNvZGUgJiYgZXZlbnQua2V5Q29kZSA9PSAxMykpICAgICB7ZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ2N0bDAwX0NvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXJfYnRuU2VhcmNoJykuY2xpY2soKTtyZXR1cm4gZmFsc2U7fSAgICAgZWxzZSByZXR1cm4gdHJ1ZTtkAgcPDxYCHhRDdHJsRm9jdXNBZnRlclNlbGVjdAUpY3RsMDBfQ29udGVudFBsYWNlSG9sZGVyV3JhcHBlcl9idG5TZWFyY2hkFgQCAw8PZBYEHgZvbmJsdXIFSEhpZGVBQ1BvcHVsYXRlX2N0bDAwX0NvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXJfc3JjaERvdmVyX3dzQXV0b0NvbXBsZXRlMR4Hb25rZXl1cAVbcmV0dXJuIEF1dG9Db21wbGV0ZUNoZWNrRGVsZXRlKGV2ZW50LCAnY3RsMDBfQ29udGVudFBsYWNlSG9sZGVyV3JhcHBlcl9zcmNoRG92ZXJfaGRuVmFsdWUnKWQCBQ8WBh4RT25DbGllbnRQb3B1bGF0ZWQFVkF1dG9Db21wbGV0ZV9DbGllbnRQb3B1bGF0ZWRfY3RsMDBfQ29udGVudFBsYWNlSG9sZGVyV3JhcHBlcl9zcmNoRG92ZXJfd3NBdXRvQ29tcGxldGUxHhRPbkNsaWVudEl0ZW1TZWxlY3RlZAVUd3NBdXRvQ29tcGxldGVfanNfc2VsZWN0ZWRfY3RsMDBfQ29udGVudFBsYWNlSG9sZGVyV3JhcHBlcl9zcmNoRG92ZXJfd3NBdXRvQ29tcGxldGUxHhJPbkNsaWVudFBvcHVsYXRpbmcFSFNob3dBQ1BvcHVsYXRlX2N0bDAwX0NvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXJfc3JjaERvdmVyX3dzQXV0b0NvbXBsZXRlMWQCCQ8PFgIfBgUpY3RsMDBfQ29udGVudFBsYWNlSG9sZGVyV3JhcHBlcl9idG5TZWFyY2hkFgQCAw8PZBYEHwcFSkhpZGVBQ1BvcHVsYXRlX2N0bDAwX0NvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXJfc3JjaE1hbmFnZXJfd3NBdXRvQ29tcGxldGUxHwgFXXJldHVybiBBdXRvQ29tcGxldGVDaGVja0RlbGV0ZShldmVudCwgJ2N0bDAwX0NvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXJfc3JjaE1hbmFnZXJfaGRuVmFsdWUnKWQCBQ8WBh8JBVhBdXRvQ29tcGxldGVfQ2xpZW50UG9wdWxhdGVkX2N0bDAwX0NvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXJfc3JjaE1hbmFnZXJfd3NBdXRvQ29tcGxldGUxHwoFVndzQXV0b0NvbXBsZXRlX2pzX3NlbGVjdGVkX2N0bDAwX0NvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXJfc3JjaE1hbmFnZXJfd3NBdXRvQ29tcGxldGUxHwsFSlNob3dBQ1BvcHVsYXRlX2N0bDAwX0NvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXJfc3JjaE1hbmFnZXJfd3NBdXRvQ29tcGxldGUxZAIND2QWBAIBDxBkEBUGFdeh15XXkteZINeT15nXldeg15nXnQzXqdeQ15nXnNeq15QP15TXptei16og15fXldenFteU16bXoteqINeQ15kg15DXnteV158a15TXptei15Qg15zXodeT16gg15TXmdeV150j15TXptei15Qg15zXodeT16gg15nXldedINeb15XXnNec16oVBgEwATEBMgEzATQCMTUUKwMGZ2dnZ2dnZGQCCQ8PZBYCHwUFyAFpZiAoKGV2ZW50LndoaWNoICYmIGV2ZW50LndoaWNoID09IDEzKSB8fCAoZXZlbnQua2V5Q29kZSAmJiBldmVudC5rZXlDb2RlID09IDEzKSkgICAgIHtkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnY3RsMDBfQ29udGVudFBsYWNlSG9sZGVyV3JhcHBlcl9idG5TZWFyY2gnKS5jbGljaygpO3JldHVybiBmYWxzZTt9ICAgICBlbHNlIHJldHVybiB0cnVlO2QCDw8PFgIeBERhdGUGAABgHGmBzAhkFgJmD2QWAmYPZBYCAgEPZBYEZg9kFgpmD2QWAgIBDw8WAh8EBQQyMDEwFgIfCAVVcmV0dXJuIERhdGVQaWNrZXJEZWxldGUoZXZlbnQsICdjdGwwMF9Db250ZW50UGxhY2VIb2xkZXJXcmFwcGVyX3NyY2hEYXRlc1BlcmlvZEZyb20nKWQCAg9kFgICAQ8PFgIfBAUBMhYCHwgFVXJldHVybiBEYXRlUGlja2VyRGVsZXRlKGV2ZW50LCAnY3RsMDBfQ29udGVudFBsYWNlSG9sZGVyV3JhcHBlcl9zcmNoRGF0ZXNQZXJpb2RGcm9tJylkAgQPZBYCAgEPDxYCHwQFAjIyFgIfCAVVcmV0dXJuIERhdGVQaWNrZXJEZWxldGUoZXZlbnQsICdjdGwwMF9Db250ZW50UGxhY2VIb2xkZXJXcmFwcGVyX3NyY2hEYXRlc1BlcmlvZEZyb20nKWQCBg9kFgICAQ8WAh8EBQbXqdeg15lkAgcPZBYCAgEPDxYCHwQFCjIyLzAyLzIwMTAWBB8IBQ92YWxpZERhdGUodGhpcykfBwVJaXNEYXRlKHRoaXMsJ2N0bDAwX0NvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXJfc3JjaERhdGVzUGVyaW9kRnJvbV9sYmxNc2cnKWQCAQ9kFgJmD2QWAmYPDxYCHwQFFteXJyDXkdeQ15PXqCDXlNeq16ki16JkZAIRDw8WAh8MBgAAYBxpgcwIZBYCZg9kFgJmD2QWAgIBD2QWBGYPZBYKZg9kFgICAQ8PFgIfBAUEMjAxMBYCHwgFU3JldHVybiBEYXRlUGlja2VyRGVsZXRlKGV2ZW50LCAnY3RsMDBfQ29udGVudFBsYWNlSG9sZGVyV3JhcHBlcl9zcmNoRGF0ZXNQZXJpb2RUbycpZAICD2QWAgIBDw8WAh8EBQEyFgIfCAVTcmV0dXJuIERhdGVQaWNrZXJEZWxldGUoZXZlbnQsICdjdGwwMF9Db250ZW50UGxhY2VIb2xkZXJXcmFwcGVyX3NyY2hEYXRlc1BlcmlvZFRvJylkAgQPZBYCAgEPDxYCHwQFAjIyFgIfCAVTcmV0dXJuIERhdGVQaWNrZXJEZWxldGUoZXZlbnQsICdjdGwwMF9Db250ZW50UGxhY2VIb2xkZXJXcmFwcGVyX3NyY2hEYXRlc1BlcmlvZFRvJylkAgYPZBYCAgEPFgIfBAUG16nXoNeZZAIHD2QWAgIBDw8WAh8EBQoyMi8wMi8yMDEwFgQfCAUPdmFsaWREYXRlKHRoaXMpHwcFR2lzRGF0ZSh0aGlzLCdjdGwwMF9Db250ZW50UGxhY2VIb2xkZXJXcmFwcGVyX3NyY2hEYXRlc1BlcmlvZFRvX2xibE1zZycpZAIBD2QWAmYPZBYCZg8PFgIfBAUW15cnINeR15DXk9eoINeU16rXqSLXomRkAhUPEA8WAh4LXyFEYXRhQm91bmRnZBAVARDXlNeb16DXodeqINeUIDE4FQECMTgUKwMBZ2RkAhkPDxYCHgtQb3N0QmFja1VybAUlL2Vwcm90b2NvbC9QVUJMSUMvU2VhcmNoUEVPbmxpbmUuYXNweGRkAhsPDxYCHw4FJS9lcHJvdG9jb2wvUFVCTElDL1NlYXJjaFBFT25saW5lLmFzcHhkZAIdDw8WBB8EBTfXnNeQINeg157XpteQ15Ug16rXldem15DXldeqINec15fXmdek15XXqSDXlNee15HXlden16kuHgdWaXNpYmxlaGRkAgkPZBYGAgEPDxYCHwQFYSDXnteZ15zXlFzXmdedOiA8Yj7XkDwvYj4sICAgICAgICDXkdeY15XXldeXINeq15DXqNeZ15vXmdedOiA8Yj7Xni0yMi8wMi8yMDEwINei15MtMjIvMDIvMjAxMDwvYj5kZAIDDw8WAh8EBQEwZGQCBw8PFgIfBGVkZAILDw8WBh8EBRzXl9eW15XXqCDXnNee16HXmiDXl9eZ16TXldepHw4FJS9lcHJvdG9jb2wvUFVCTElDL1NlYXJjaFBFT25saW5lLmFzcHgfD2hkZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WCQU4Y3RsMDAkQ29udGVudFBsYWNlSG9sZGVyV3JhcHBlciRzcmNoQ0tfaW50ZXJydXB0X3NwZWFrZXIFMWN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXIkcmRvU2VhcmNoQnlOdW1iZXIFMWN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXIkcmRvU2VhcmNoQnlOdW1iZXIFL2N0bDAwJENvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXIkcmRvU2VhcmNoQnlUZXh0BTFjdGwwMCRDb250ZW50UGxhY2VIb2xkZXJXcmFwcGVyJHNyY2hfcmRvX1llc2hpdml0BTFjdGwwMCRDb250ZW50UGxhY2VIb2xkZXJXcmFwcGVyJHNyY2hfcmRvX1llc2hpdml0BS5jdGwwMCRDb250ZW50UGxhY2VIb2xkZXJXcmFwcGVyJHNyY2hfcmRvX1RvcmltBTxjdGwwMCRDb250ZW50UGxhY2VIb2xkZXJXcmFwcGVyJHNyY2hEYXRlc1BlcmlvZEZyb20kYnRuUG9wVXAFOmN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcldyYXBwZXIkc3JjaERhdGVzUGVyaW9kVG8kYnRuUG9wVXCpRkP1sigDyMUEQRUVvHjI2IVBFw%3D%3D&ctl00%24ContentPlaceHolderWrapper%24STATUS=srch_rdo_Torim&ctl00%24ContentPlaceHolderWrapper%24SearchSubjectRDO=rdoSearchByText&ctl00%24ContentPlaceHolderWrapper%24btnSearch=%D7%97%D7%A4%D7%A9&ctl00%24ContentPlaceHolderWrapper%24srchDatesPeriodFrom%24txtDate='+from_day+'%2F'+from_month+'%2F'+from_year+'&ctl00%24ContentPlaceHolderWrapper%24srchDatesPeriodFrom%24txtDay='+from_day+'&ctl00%24ContentPlaceHolderWrapper%24srchDatesPeriodFrom%24txtMonth='+from_month+'&ctl00%24ContentPlaceHolderWrapper%24srchDatesPeriodFrom%24txtYear='+from_year+'&ctl00%24ContentPlaceHolderWrapper%24srchDatesPeriodTo%24txtDate='+to_day+'%2F'+to_month+'%2F'+to_year+'&ctl00%24ContentPlaceHolderWrapper%24srchDatesPeriodTo%24txtDay='+to_day+'&ctl00%24ContentPlaceHolderWrapper%24srchDatesPeriodTo%24txtMonth='+to_month+'&ctl00%24ContentPlaceHolderWrapper%24srchDatesPeriodTo%24txtYear='+to_year+'&ctl00%24ContentPlaceHolderWrapper%24srchDover%24hdnValue=&ctl00%24ContentPlaceHolderWrapper%24srchDover%24myTextBox=&ctl00%24ContentPlaceHolderWrapper%24srchExcludeFreeText=&ctl00%24ContentPlaceHolderWrapper%24srchFreeText='+search_text+'&ctl00%24ContentPlaceHolderWrapper%24srchKnesset=18&ctl00%24ContentPlaceHolderWrapper%24srchManager%24hdnValue=&ctl00%24ContentPlaceHolderWrapper%24srchManager%24myTextBox=&ctl00%24ContentPlaceHolderWrapper%24srchSubject=&ctl00%24ContentPlaceHolderWrapper%24srchSubjectType=0&ctl00%24ContentPlaceHolderWrapper%24srch_SubjectNumber=&hiddenInputToUpdateATBuffer_CommonToolkitScripts=1'
            page = urllib2.urlopen(url,params).read()
            m = re.search('ProtEOnlineLoad\((.*), \'false\'\);', page)
            if not m:
                logger.debug("couldn't find vote in synched protocol\nvote.id=%s\nvote.title=%s\nsearch_text=%s", str(v.id), v.title, search_text)
                return
            l = Link(title=u'פרוטוקול מסונכרן (וידאו וטקסט) של הישיבה', url='http://online.knesset.gov.il/eprotocol/PLAYER/PEPlayer.aspx?ProtocolID=%s' % m.group(1), content_type=ContentType.objects.get_for_model(v), object_pk=str(v.id))
            l.save()
        except Exception, e:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            logger.error("%s%s", ''.join(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)), '\nsearch_text='+search_text.encode('utf8')+'\nvote.title='+v.title.encode('utf8'))

    def check_vote_mentioned_in_cm(self, v, cm):
        m = v.title[v.title.find(' - ')+2:]
        v_search_text = self.get_search_string(m.encode('utf8'))
        cm_search_text = self.get_search_string(cm.protocol_text.encode('utf8')).replace('\n','')
        if cm_search_text.find(v_search_text)>=0:
            cm.votes_mentioned.add(v)

    def find_votes_in_cms(self):
        for cm in CommitteeMeeting.objects.all():
            for v in Vote.objects.all():
                self.check_vote_mentioned_in_cm(v, cm)
            
    def get_protocols_page(self, page, page_num):
        FILES_BASE_URL = "http://www.knesset.gov.il/protocols/"
        res = []
        max_linked_page = max([int(r) for r in re.findall("'Page\$(\d*)",page)])
        last_page = False        
        if max_linked_page < page_num:
            last_page = True

        # trim the page to the results part
        start = page.find(r'id="gvProtocol"')
        end = page.find(r'javascript:__doPostBack')
        page = page[start:end]
        date_text = ''
        comittee = ''
        subject = ''
        # find interesting parts
        matches = re.findall(r'<span id="gvProtocol(.*?)</span>|OpenDoc(.*?)\);',page, re.DOTALL)
        for (span,link) in matches:
            if len(span): # we are parsing a matched span - committee info
                if span.find(r'ComName')>0:
                    comittee = span[span.find(r'>')+1:]
                if span.find(r'lblDate')>0:
                    date_text = span[span.find(r'>')+1:]
                if span.find(r'lblSubject')>0:
                    if span.find(r'<Table')>0: # this subject is multiline so they show it a a table
                        subject = ' '.join(re.findall(r'>([^<]*)<',span)) # extract text only from all table elements
                    else:
                        subject = span[span.find(r'>')+1:] # no table, just take the text
            else: # we are parsing a matched link - comittee protocol url
                if link.find(r'html')>0:
                    html_url = FILES_BASE_URL + re.search(r"'\.\./([^']*)'", link).group(1)
                    res.append([date_text, comittee, subject, html_url]) # this is the last info we need, so add data to results        
                    date_text = ''
                    comittee = ''
                    subject = ''
        return (last_page, res)

    def get_protocols(self, max_page=10):        
        SEARCH_URL = "http://www.knesset.gov.il/protocols/heb/protocol_search.aspx"
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)


        # get the search page to extract legal "viewstate" and "event validation" strings. need to pass them so the search will work
        page = urllib2.urlopen(SEARCH_URL).read().decode('windows-1255').encode('utf-8')
        
        event_validation = urllib2.quote(re.search(r'id="__EVENTVALIDATION" value="([^"]*)"', page).group(1)).replace('/','%2F')
        view_state = urllib2.quote(re.search(r'id="__VIEWSTATE" value="([^"]*)"', page).group(1)).replace('/','%2F')        

        # define date range
        params = "__EVENTTARGET=DtFrom&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%s&ComId=-1&knesset_id=-1&DtFrom=24%%2F02%%2F2009&DtTo=&subj=&__EVENTVALIDATION=%s" % (view_state, event_validation)
        page = urllib2.urlopen(SEARCH_URL,params).read().decode('windows-1255').encode('utf-8')
        event_validation = urllib2.quote(re.search(r'id="__EVENTVALIDATION" value="([^"]*)"', page).group(1)).replace('/','%2F')
        view_state = urllib2.quote(re.search(r'id="__VIEWSTATE" value="([^"]*)"', page).group(1)).replace('/','%2F')        

        # hit the search
        params = "btnSearch=%%E7%%E9%%F4%%E5%%F9&__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%s&ComId=-1&knesset_id=-1&DtFrom=24%%2F02%%2F2009&DtTo=&subj=&__EVENTVALIDATION=%s" % (view_state, event_validation)
        page = urllib2.urlopen(SEARCH_URL,params).read().decode('windows-1255').encode('utf-8')
        event_validation = urllib2.quote(re.search(r'id="__EVENTVALIDATION" value="([^"]*)"', page).group(1)).replace('/','%2F')
        view_state = urllib2.quote(re.search(r'id="__VIEWSTATE" value="([^"]*)"', page).group(1)).replace('/','%2F')        
        page_num = 1        
        (last_page, page_res) = self.get_protocols_page(page, page_num)
        res = page_res[:]

        while (not last_page) and (page_num < max_page):
            page_num += 1 
            params = "__EVENTTARGET=gvProtocol&__EVENTARGUMENT=Page%%24%d&__LASTFOCUS=&__VIEWSTATE=%s&ComId=-1&knesset_id=-1&DtFrom=24%%2F02%%2F2009&DtTo=&subj=&__EVENTVALIDATION=%s" % (page_num, view_state, event_validation)
            page = urllib2.urlopen(SEARCH_URL,params).read().decode('windows-1255').encode('utf-8')
            # update EV and VS    
            event_validation = urllib2.quote(re.search(r'id="__EVENTVALIDATION" value="([^"]*)"', page).group(1)).replace('/','%2F')
            view_state = urllib2.quote(re.search(r'id="__VIEWSTATE" value="([^"]*)"', page).group(1)).replace('/','%2F')
            # parse the page            
            (last_page, page_res) = self.get_protocols_page(page, page_num)
            res.extend(page_res)


        for (date_string, com, topic, link) in res:
            (c, created) = Committee.objects.get_or_create(name=com)
            if created:
                c.save()
            r = re.search("(\d\d)/(\d\d)/(\d\d\d\d)", date_string)
            d = datetime.date(int(r.group(3)), int(r.group(2)), int(r.group(1)))
            (cm, created) = CommitteeMeeting.objects.get_or_create(committee=c, date_string=date_string, date=d, topics=topic)
            if not created:
                continue
            cm.protocol_text = self.get_committee_protocol_text(link)
            cm.save()
            try:
                r = re.search("חברי הוועדה(.*?)\n\n".decode('utf8'),cm.protocol_text, re.DOTALL).group(1)
                s = r.split('\n')
                s = [s0.replace(' - ',' ').replace("'","").replace(u"”",'').replace('"','').replace("`","").replace("(","").replace(")","").replace(u'\xa0',' ').replace(' ','-') for s0 in s]
                for m in Member.objects.all():
                    for s0 in s:
                        if s0.find(m.name_with_dashes())>=0:
                            print "found %s in %s" % (m.name, str(cm.id))
                            cm.mks_attended.add(m)                        
            except Exception, e:
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                logger.debug("%s%s", ''.join(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)), '\nCommitteeMeeting.id='+str(cm.id))

            cm.save()
            


    def get_committee_protocol_text(self, url):
        if url.find('html'):
            url = url.replace('html','rtf')
        file_str = StringIO()
        file_str.write(urllib2.urlopen(url).read())
        try:
            doc = Rtf15Reader.read(file_str)
        except Exception:
            return ''
        text = []
        attended_list = False
        for paragraph in doc.content:
            for sentence in paragraph.content:
                if 'bold' in sentence.properties and attended_list:
                    attended_list = False
                    text.append('')
                if 'מוזמנים'.decode('utf8') in sentence.content[0] and 'bold' in sentence.properties:
                    attended_list = True                
                text.append(sentence.content[0])
        all_text = '\n'.join(text)
        return re.sub(r'\n:\n',r':\n',all_text)

    def get_full_text(self,v):
        try:
            l = Link.objects.get(object_pk=str(v.id), title=u'מסמך הצעת החוק באתר הכנסת')
        except Exception:
            return
        try:
            if l.url.endswith('.rtf'):
                file_str = StringIO()
                file_str.write(urllib2.urlopen(l.url).read())
                doc = Rtf15Reader.read(file_str)
                content_list = []
                is_bold = False
                for j in [1,2]:
                    for i in range(len(doc.content[j].content)):
                        part = doc.content[j].content[i]
                        if 'bold' in part.properties:           # this part is bold
                            if not is_bold:                          # last part was not bold
                                content_list.append('<br/><b>')         # add new line and bold
                                is_bold = True                          # remember that we are now in bold
                            content_list.append(part.content[0]+' ') # add this part
                            
                        else:                                   # this part is not bold
                            if len(part.content[0]) <= 1:           # this is a dummy node, ignore it
                                pass
                            else:                                   # this is a real node
                                if is_bold:                         # last part was bold. need to unbold
                                    content_list.append('</b>')
                                    is_bold = False
                                content_list.append('<br/>'+part.content[0]) #add this part in a new line

                    content_list.append('<br/>')

                v.full_text = ''.join(content_list)
                v.save()
        except Exception, e:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            logger.error("%s%s", ''.join(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)), '\nvote.title='+v.title.encode('utf8'))

    def dump_to_file(self):
        f = open('votes.tsv','wt')
        for v in Vote.objects.filter(time__gte=datetime.date(2009,2,24)):
            if (v.full_text_url != None):
                link = v.full_text_url.encode('utf-8')
            else:
                link = ''            
            if (v.summary != None):
                summary = v.summary.encode('utf-8')
            else:
                summary = ''            
            #for_ids = ",".join([str(m.id) for m in v.votes.filter(voteaction__type='for').all()])
            #against_ids = ",".join([str(m.id) for m in v.votes.filter(voteaction__type='against').all()])
            #f.write("%d\t%s\t%s\t%s\t%s\t%s\t%s\n" % (v.id,v.title.encode('utf-8'),v.time_string.encode('utf-8'),summary, link, for_ids, against_ids))
            f.write("%d\t%s\t%s\t%s\t%s\n" % (v.id, str(v.time), v.title.encode('utf-8'), summary, link))
        f.close()

        f = open('votings.tsv','wt')
        for v in Vote.objects.filter(time__gte=datetime.date(2009,2,24)):
            for va in v.voteaction_set.all():
                f.write("%d\t%d\t%s\n" % (v.id, va.member.id, va.type))
        f.close()

        f = open('members.tsv','wt')
        for m in Member.objects.filter(end_date__gte=datetime.date(2009,2,24)):
            f.write("%d\t%s\t%s\n" % (m.id, m.name.encode('utf-8'), m.Party().__unicode__().encode('utf-8')))
        f.close()


    def handle_noargs(self, **options):
    
        all_options = options.get('all', False)
        download = options.get('download', False)
        load = options.get('load', False)
        process = options.get('process', False)
        dump_to_file = options.get('dump-to-file', False)
        update = options.get('update', False)
        if all_options:
            download = True
            load = True
            process = True
            dump_to_file = True

        if (all([not(all_options),not(download),not(load),not(process),not(dump_to_file),not(update)])):
            print "no arguments found. doing nothing. \ntry -h for help.\n--all to run the full syncdata flow.\n--update for an online dynamic update."

        if download:
            print "beginning download phase"
            self.download_all()    
            #self.get_laws_data()
        
        if load:
            print "beginning load phase"
            self.update_members_from_file()
            self.update_db_from_files()

        if process:
            print "beginning process phase"
            self.calculate_votes_importances()
            #self.calculate_correlations()

        if dump_to_file:
            print "writing votes to tsv file"
            self.dump_to_file()

        if update:
            self.update_votes()
            self.update_laws_data()

def update_vote_properties(v):
    party_id_member_count_coalition = Party.objects.annotate(member_count=Count('members')).values_list('id','member_count','is_coalition')
    party_ids = [x[0] for x in party_id_member_count_coalition]
    party_member_count = [x[1] for x in party_id_member_count_coalition]
    party_is_coalition = dict(zip(party_ids, [x[2] for x in party_id_member_count_coalition] ))

    for_party_ids = [va.member.current_party.id for va in v.for_votes()]    
    party_for_votes = [sum([x==id for x in for_party_ids]) for id in party_ids]    

    against_party_ids = [va.member.current_party.id for va in v.against_votes()]
    party_against_votes = [sum([x==id for x in against_party_ids]) for id in party_ids]

    party_stands_for = [float(fv)>0.66*(fv+av) for (fv,av) in zip(party_for_votes, party_against_votes)]
    party_stands_against = [float(av)>0.66*(fv+av) for (fv,av) in zip(party_for_votes, party_against_votes)]
    
    party_stands_for = dict(zip(party_ids, party_stands_for))
    party_stands_against = dict(zip(party_ids, party_stands_against))

    coalition_for_votes = sum([x for (x,y) in zip(party_for_votes,party_ids) if party_is_coalition[y]])
    coalition_against_votes = sum([x for (x,y) in zip(party_against_votes,party_ids) if party_is_coalition[y]])
    opposition_for_votes = sum([x for (x,y) in zip(party_for_votes,party_ids) if not party_is_coalition[y]])
    opposition_against_votes = sum([x for (x,y) in zip(party_against_votes,party_ids) if not party_is_coalition[y]])

    coalition_stands_for = (float(coalition_for_votes)>0.66*(coalition_for_votes+coalition_against_votes)) 
    coalition_stands_against = float(coalition_against_votes)>0.66*(coalition_for_votes+coalition_against_votes)
    opposition_stands_for = float(opposition_for_votes)>0.66*(opposition_for_votes+opposition_against_votes)
    opposition_stands_against = float(opposition_against_votes)>0.66*(opposition_for_votes+opposition_against_votes)


    against_party_count = 0
    for va in VoteAction.objects.filter(vote=v):
        dirt = False
        if party_stands_for[va.member.current_party.id] and va.type=='against':
            va.against_party = True
            against_party_count += 1
            dirt = True
        if party_stands_against[va.member.current_party.id] and va.type=='for':
            va.against_party = True
            dirt = True
        if va.member.Party().is_coalition:
            if (coalition_stands_for and va.type=='against') or (coalition_stands_against and va.type=='for'):
                va.against_coalition = True
                dirt = True
        else:
            if (opposition_stands_for and va.type=='against') or (opposition_stands_against and va.type=='for'):
                va.against_opposition = True
                dirt = True
        if dirt:
            va.save()

    v.controversy = min(v.for_votes_count(), v.against_votes_count())
    v.against_party = against_party_count
    v.votes_count = VoteAction.objects.filter(vote=v).count()
    v.save()
