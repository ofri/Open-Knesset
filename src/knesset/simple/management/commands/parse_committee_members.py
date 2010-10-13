#### encoding: utf-8 ####

import sys
import urllib2
import re

member_re = re.compile("/mk/heb/mk\.asp\?ID=(\d+)")

committees = { u'הכנסת' : 'http://portal.knesset.gov.il/com1knesset/he-il', 
               u'החוקה' : 'http://knesset.gov.il/huka/',
               }

def parse_committee_members():
    retval = {}
    for hint,url  in committees.iteritems():
        data = urllib2.urlopen(url).read()
        print len(data)
        member_ids = [int(x) for x in member_re.findall(data)]
        print hint, member_ids
        chairperson_id = member_ids[0]
        member_ids = member_ids[1:]
        
        retval[hint] = { 'chairperson_id':chairperson_id,
                         'member_ids':member_ids}
    
    return retval

def update_committee_members_db(data):
    for hint, memberinfo in data.iteritems():
        cm = Committee.objects.get(name__icontains=hint)
        cm.members.clear()
        m = Member.objects.get(id=memberinfo['chairperson_id'])
        cm.members.add(m)
        cm.chairperson = m
        cm.save() 
        for m in memberinfo['member_ids']:
            m = Member.objects.get(id=m)
            cm.members.add(m)
        
if __name__=="__main__":
    print parse_committee_members()
    #update_committee_members_db(parse_committee_members)
    