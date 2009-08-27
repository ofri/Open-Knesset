 # This Python file uses the following encoding: utf-8
import os,sys,traceback
from django.core.management.base import NoArgsCommand
from optparse import make_option
from django.conf import settings

import urllib2,urllib
import re
import gzip
import simplejson
import datetime

from knesset.simple.models import *
from django.db import connection
from django.db.models import Max

DATA_ROOT = getattr(settings, 'DATA_ROOT',
                    os.path.join(settings.PROJECT_ROOT, 'data'))

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
        
    )
    help = "Downloads data from sources, parses it and loads it to the Django DB."

    requires_model_validation = False

    last_id = 1

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
            r = re.search("""Href=\"(.*?)\">""",line)
            if r != None:
                link = 'http://www.knesset.gov.il/privatelaw/' + r.group(1)
            r = re.search("""<td class="LawText1">(.*)</td>""",line)
            if r != None:
                name = r.group(1)
                if len(name)>0:
                    names.append(name)
                    links.append(link)
                    exps.append('')
                    count += 1
            if re.search("""arrResume\[\d*\]""",line) != None:
                r = re.search("""\"(.*)\"""",line)
                if r != None:
                    exps[count] += r.group(1).replace('\t',' ')

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

    def get_votes_data(self):
        f  = gzip.open(os.path.join(DATA_ROOT, 'results.tsv.gz'), "ab")
        f2 = gzip.open(os.path.join(DATA_ROOT, 'votes.tsv.gz'),"ab")
        r = range(self.last_id+1,12110) # this is the range of page ids to go over. currently its set manually.
        for id in r:
            page = self.read_votes_page(id)
            title = self.get_page_title(page)
            if(title == """הצבעות במליאה-חיפוש"""): # found no vote with this id
                print "no vote found at id %d" % id
            else:
                count_for = 0
                count_against = 0
                count_abstain = 0
                count_no_vote = 0
                (name,date) = self.get_vote_data(page)
                results = self.read_member_votes(page)
                for i in results:
                    f.write("%d\t%s\t%s\t%s\t%s\t%s\n" % (id,name,date,i[0],i[1],i[2]))
                    if(i[2]=="for"):
                        count_for += 1
                    if(i[2]=="against"):
                        count_against += 1
                    if(i[2]=="abstain"):
                        count_abstain += 1
                    if(i[2]=="no-vote"):
                        count_no_vote += 1
                f2.write("%d\t%s\t%s\t%d\t%d\t%d\t%d\n" % (id, name, date, count_for,count_against,count_abstain,count_no_vote))
                print "downloaded data with vote id %d" % id
            print " %.2f%% done" % ( (100.0*(float(id)-r[0]))/(r[-1]-r[0]) )
        f.close()
        f2.close()        
    
    def download_all(self):
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
            self.last_id = 0
            print "votes file does not exist. will download all votes from knesset (may take some time...)"
            return            
        content = f.read().split('\n')
        for line in content:
            if(len(line)<2):
                continue
            s = line.split('\t')
            vote_id = int(s[0])
            if vote_id > self.last_id:
                self.last_id = vote_id
        print "last id found in local files is %d. " % self.last_id
        f.close()
        

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
        print "Update DB From Files"

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

            f = gzip.open(os.path.join(DATA_ROOT, 'results.tsv.gz'))
            content = f.read().split('\n')
            parties = dict() # key: party-name; value: Party
            members = dict() # key: member-name; value: Member
            votes   = dict() # key: id; value: Vote
            memberships = dict() # key: (member.id,party.id)
            current_vote = None # used to track what vote we are on, to create vote objects only for new votes
            current_max_src_id = Vote.objects.aggregate(Max('src_id'))['src_id__max']
            if current_max_src_id == None: # the db contains no votes, meanins its empty
                current_max_src_id = 0
            print "%s processing data. current_max_src_id = %d" % (str(datetime.datetime.now()), current_max_src_id)
            for line in content:
                if(len(line)<2):
                    continue
                s = line.split('\t')
                
                vote_id = int(s[0])

                if vote_id < current_max_src_id: # skip votes already parsed.
          
#                if vote_id > 500: # TEMP
                    continue  
             
                vote_label = s[1]
                vote_label_for_search = self.get_search_string(vote_label)

                relevant = False

                # some votes are intersting, some are just stupid. so lets load only something that has potential to be interesting
                if(vote_label.find('אישור החוק') >= 0):
                    relevant = True
                #if(vote_label.find('קריאה שניה') >= 0):
                #    relevant = True
                #if(vote_label.find('הצבעה') >= 0):
                #    relevant = True

                if not relevant:
                    continue

                vote_time_string = s[2].replace('&nbsp;',' ')
                for i in self.heb_months:
                    if i in vote_time_string:
                        month = self.heb_months.index(i)+1
                day = re.search("""(\d\d?)""", vote_time_string).group(1)
                year = re.search("""(\d\d\d\d)""", vote_time_string).group(1)
                vote_hm = datetime.datetime.strptime ( vote_time_string.split(' ')[-1], "%H:%M" )
                vote_date = datetime.date(int(year),int(month),int(day))
                vote_time = datetime.datetime(int(year), int(month), int(day), vote_hm.hour, vote_hm.minute)
                
                voter = s[3]
                voter_party = s[4]

                # transform party names to canonical form
                if(voter_party in self.party_aliases):
                    voter_party = self.party_aliases[voter_party]

                vote = s[5]

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
                    m,created = Member.objects.get_or_create(name=voter)
                    members[voter] = m
                m.party = p;
                #if created: # again, unicode magic
                #    m = Member.objects.get(name=voter)
                # use this vote's date to update the member's dates.
                if (m.start_date is None) or (m.start_date > vote_date):
                    m.start_date = vote_date
                if (m.end_date is None) or (m.end_date < vote_date):
                    m.end_date = vote_date
                if created: # save on first time, so it would have an id, be able to link, etc. all other updates are saved in the end
                    m.save()
        
                    
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
                    
                # create/get a vote object for this vote
                if (current_vote == None) or (vote_id != current_vote.src_id): # we are parsing a new vote. need to create new object
                    if vote_id in votes:
                        v = votes[vote_id]
                        created = False
                    else:
                        try:
                            v = Vote.objects.get(src_id=vote_id)                
                            created = False
                        except:
                            v = Vote(title=vote_label, time_string=vote_time_string, importance=1, src_id=vote_id, time=vote_time)
                            v.save()
                            created = True

                    if created: 
                        for law in laws:
                            (law_name,law_name_for_search,law_exp,law_link) = law
                            if vote_label_for_search.find(law_name_for_search) >= 0:
                                #print 'kaching! match on %s' % law_name
                                v.summary = law_exp
                                v.full_text_url = law_link
                        votes[vote_id] = v
                    current_vote = v
                # and add the current member's vote
                if vote=='for':
                    current_vote.voted_for.add(m)
                if vote=='against':
                    current_vote.voted_against.add(m)
                if vote=='abstain':
                    current_vote.voted_abstain.add(m)
                if vote=='no-vote':
                    current_vote.didnt_vote.add(m)
                if created:
                    current_vote.save()
                
            print "%s done" % str(datetime.datetime.now())
            print "%s saving data: %d parties, %d members, %d memberships, %d votes " % (str(datetime.datetime.now()), len(parties), len(members), len(memberships), len(votes) )
            for p in parties:
                parties[p].save()
            for m in members:
                members[m].save()
            for ms in memberships:
                memberships[ms].save()
            for v in votes:
                votes[v].save()
            print "%s done" % str(datetime.datetime.now())
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print "error: "
            traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback, limit=2, file=sys.stdout)

    def calculate_votes_importances(self):
        """
        Calculates votes importances. currently uses rule of thumb: number of voters against + number of voters for / 120.
        """    
        for v in Vote.objects.all():
            v.importance = float(v.voted_for.count() + v.voted_against.count()) / 120
            v.save()
        
    def calculate_correlations(self):
        """
        Calculates member pairs correlation on votes.
        """
        # TODO: refactor the hell out of this one...
        print "Calculate Correlations"
        try:     
            cursor = connection.cursor()
            print "%s truncate correlations table" % str(datetime.datetime.now())
            Correlation.objects.all().delete()
            print "%s calculate correlations"  % str(datetime.datetime.now())
            cursor.execute("""insert into simple_correlation (m1_id,m2_id,score) (
                select m1 as m1_id, m2 as m2_id,sum(score) as score from (
                select a1.member_id as m1,a2.member_id as m2, count(*) as score from (
                (select * from simple_vote_voted_for) a1,
                (select * from simple_vote_voted_for) a2
                ) where a1.vote_id = a2.vote_id and a1.member_id < a2.member_id group by a1.member_id,a2.member_id
                union
                select a1.member_id as m1,a2.member_id as m2, count(*) as score from (
                (select * from simple_vote_voted_against) a1,
                (select * from simple_vote_voted_against) a2
                ) where a1.vote_id = a2.vote_id and a1.member_id < a2.member_id group by a1.member_id,a2.member_id
                union
                select a1.member_id as m1,a2.member_id as m2, -count(*) as score from (
                (select * from simple_vote_voted_for) a1,
                (select * from simple_vote_voted_against) a2
                ) where a1.vote_id = a2.vote_id and a1.member_id < a2.member_id group by a1.member_id,a2.member_id
                union
                select a1.member_id as m1,a2.member_id as m2, -count(*) as score from (
                (select * from simple_vote_voted_against) a1,
                (select * from simple_vote_voted_for) a2
                ) where a1.vote_id = a2.vote_id and a1.member_id < a2.member_id group by a1.member_id,a2.member_id
                
                ) a group by m1,m2
                )""".replace('\n',''))
            print "%s done"  % str(datetime.datetime.now())
            print "%s normalizing correlation"  % str(datetime.datetime.now())
            cursor.execute("""update simple_correlation,
                (select member_id,sum(vote_count) as vote_count from (
                select member_id,count(*) as vote_count from simple_vote_voted_for group by member_id
                union
                select member_id,count(*) as vote_count from simple_vote_voted_against group by member_id
                ) a 
                group by member_id) a1,
                (select member_id,sum(vote_count) as vote_count from (
                select member_id,count(*) as vote_count from simple_vote_voted_for group by member_id
                union
                select member_id,count(*) as vote_count from simple_vote_voted_against group by member_id
                ) a 
                group by member_id) a2
                set simple_correlation.normalized_score = simple_correlation.score / sqrt(a1.vote_count) / sqrt(a2.vote_count)*100 
                where simple_correlation.m1_id = a1.member_id and simple_correlation.m2_id = a2.member_id""")

        except Exception,e:
            print "error: %s" % e
     

    def read_votes_page(self,voteId, retry=0):
        """
        Gets a votes page from the knesset website.
        returns is as a string (utf encoded)
        """
        url = "http://www.knesset.gov.il/vote/heb/Vote_Res_Map.asp?vote_id_t=%d" % voteId
        try:        
            urlData = urllib2.urlopen(url)
            page = urlData.read().decode('windows-1255').encode('utf-8')
        except exception,e:
            print "ERROR: %s" % e
            if retry < 5:
                print "waiting some time and trying again... (# of retries = %d)" % retry+1
                page = read_votes_page(self,voteId, retry+1)
            else:
                return None
        return page

    def read_member_votes(self,page):
        """
        Returns a tuple of (name, party, vote) describing the vote found in page, where:
         name is a member name
         party is the member's party
         vote is 'for','against','abstain' or 'no-vote'
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
                party = re.search("""DataText4>([^<]*)</td>""",i).group(1);
                party = re.sub("""&nbsp;""", " ", party)
                if(party == """ " """):
                    party = last_party
                else:
                    last_party = party 
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
        Returns name and date from a vote page
        """
        name = re.search("""שם החוק: </td>[^<]*<[^>]*>([^<]*)<""", page).group(1)
        name = name.replace("\t"," ")
        name = name.replace("\n"," ")
        name = name.replace("\r"," ")
        name = name.replace("&nbsp;"," ")
        date = re.search("""תאריך: </td>[^<]*<[^>]*>([^<]*)<""",page)
        return (name, date.group(1))

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
        

    def handle_noargs(self, **options):
    
        all_options = options.get('all', False)
        download = options.get('download', False)
        load = options.get('load', False)
        process = options.get('process', False)
        dump_to_file = options.get('dump-to-file', False)
        if all_options:
            download = True
            load = True
            process = True
            dump_to_file = True

        if (not(all_options) and not(download) and not(load) and not(process) and not(dump_to_file)):
            print "no arguments found. doing nothing. try -h for help, or --all to run the full syncdb"

        if download:
            print "beginning download phase"
            self.update_last_downloaded_vote_id()
            self.download_all()    
        
        if load:
            print "beginning load phase"
            self.update_db_from_files()

        if process:
            print "beginning process phase"
            self.calculate_votes_importances()
            self.calculate_correlations()

        if dump_to_file:
            print "writing votes to tsv files"
            f = open('votes.tsv','wt')
            for v in Vote.objects.all():
                if (v.full_text_url != None):
                    link = v.full_text_url.encode('utf-8')
                else:
                    link = ''            
                if (v.summary != None):
                    summary = v.summary.encode('utf-8')
                else:
                    summary = ''            
                for_ids = ",".join([str(m) for m in v.voted_for.all()])
                against_ids = ",".join([str(m) for m in v.voted_for.all()])
                f.write("%d\t%s\t%s\t%s\t%s\t%s\t%s\n" % (v.id,v.title.encode('utf-8'),v.time_string.encode('utf-8'),summary, link, for_ids, against_ids))
            f.close()

        
