 # This Python file uses the following encoding: utf-8

import socket
import sys
import gzip
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append('%s/../' % base_dir)
sys.path.append('%s/../knesset/' % base_dir)
sys.path.append('%s/../knesset/simple' % base_dir)

import MySQLdb
import os
import re
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = 'knesset.settings'
from django.db import transaction
from django.db import connection

from knesset.simple.models import *

hebMonths = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר']

partyAliases = {'עבודה':'העבודה',
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

def UpdateDbFromFiles():
    print "updatedb/UpdateDbFromFiles"
    try:
        f = gzip.open('data/results.tsv.gz')
        content = f.read().split('\n')
        print "%s entering data" % str(datetime.datetime.now())
        for line in content:
            #print line
            if(len(line)<2):
                continue
            s = line.split('\t')
            
            vote_id = s[0]
            vote_label = s[1]
            relevant = False
            if(vote_label.find('אישור החוק') >= 0):
                relevant = True
            if(vote_label.find('קריאה שניה') >= 0):
                relevant = True
            if(vote_label.find('הצבעה') >= 0):
                relevant = True
            
            if not relevant:
                continue
            vote_time_string = s[2].replace('&nbsp;',' ')
            #print vote_time_string
            for i in hebMonths:
                if i in vote_time_string:
                    month = hebMonths.index(i)+1
            day = re.search("""(\d\d?)""", vote_time_string).group(1)
            year = re.search("""(\d\d\d\d)""", vote_time_string).group(1)
            vote_date = datetime.date(int(year),int(month),int(day))
            voter = s[3]
            voter_party = s[4]
            if(voter_party in partyAliases):
                voter_party = partyAliases[voter_party]
            vote = s[5]
            #print "looking for party %s" % voter_party
            p,created = Party.objects.get_or_create(name=voter_party)
            #print created
            if created:
                #print "party created: %s" % voter_party
                p = Party.objects.get(name=voter_party)
            
            if (p.start_date is None) or (p.start_date > vote_date):
                p.start_date = vote_date
            if (p.end_date is None) or (p.end_date < vote_date):
                p.end_date = vote_date
            p.save()
            
            #print "looking for member %s" % voter
            m,created = Member.objects.get_or_create(name=voter)
            #print created
            m.party = p;
            #print m.party
            if created:
                #print "member created: %s" % voter
                m = Member.objects.get(name=voter)
            if (m.start_date is None) or (m.start_date > vote_date):
                m.start_date = vote_date
            if (m.end_date is None) or (m.end_date < vote_date):
                m.end_date = vote_date
            m.save()
                
            #print "looking for membership %s-%s" % (voter,voter_party)
            ms,created = Membership.objects.get_or_create(member=m,party=p)
            if created:
                #print "membership created"
                ms = Membership.objects.get(member=m,party=p)
            if (ms.start_date is None) or (ms.start_date > vote_date):
                ms.start_date = vote_date
            if (ms.end_date is None) or (ms.end_date < vote_date):
                ms.end_date = vote_date
            ms.save()    
                
            v,created = Vote.objects.get_or_create(title=vote_label, time_string=vote_time_string)
            if created:
                v = Vote.objects.get(title=vote_label, time_string=vote_time_string)
                v.time = vote_date
            #print "vote %s on %s" % (vote,v)
            if vote=='for':
                v.voted_for.add(m)
            if vote=='against':
                v.voted_against.add(m)
            if vote=='abstain':
                v.voted_abstain.add(m)
            if vote=='no-vote':
                v.didnt_vote.add(m)
            #print "v.save()"
            v.save()
            
        print "%s done" % str(datetime.datetime.now())
    except Exception,e:
        print "error: %s" % e
        
def CalculateCorrelations():
    print "updatedb/CalculateCorrelations"
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
    
if __name__ == "__main__":
    if len(sys.argv)==1:
        UpdateDbFromFiles()
        CalculateCorrelations()
    else:
        if sys.argv[1] == 'update':
            UpdateDbFromFiles()
        if sys.argv[1] == 'calc':
            CalculateCorrelations()
