#### encoding: cp1255 ####

import urllib2
import re
import logging
logger = logging.getLogger("open-knesset.parse_committee_members")

from mks.models import Member
from committees.models import Committee 
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    args = ''
    help = 'Parses commitee members from the Knesset website'
        
    def parse_committee_members(self):
        retval = {}
        
        url = 'http://knesset.gov.il/committees/heb/CommitteeHistoryByKnesset.asp?knesset=18'

        data = urllib2.urlopen(url).read()

        member_re = re.compile("/mk/heb/mk\.asp\?mk_individual_id_t=(\d+)")
        com_re = re.compile('/committees/heb/CommitteeHistoryByCommittee.asp\?com')
        com_name_re = re.compile('<b>([^<]+)</b>')
    
        # by committees:
        data = com_re.split(data)[1:]
    
        for comdata in data:
        
            com_name = com_name_re.findall(comdata)[0].decode('cp1255')
            #print com_name    
            
            sections = comdata.split('<BR>')
            chairpersons = members = replacements = []
            for section in sections:
                if '\xe7\xe1\xf8\xe9 \xe4\xe5\xe5\xf2\xe3\xe4' in section:
                    members = member_re.findall(section)
                elif '\xe9\xe5\xf9\xe1/\xfa \xf8\xe0\xf9 \xe4\xe5\xe5\xf2\xe3\xe4' in section:
                    chairpersons = member_re.findall(section)
                elif '\xee\xee\xec\xe0\xe9 \xee\xf7\xe5\xed \xe1\xe5\xe5\xf2\xe3\xe4' in section:
                    replacements = member_re.findall(section)
                
            chairpersons = set(chairpersons)
            members = set(members)
            replacements = set(replacements)
            members = members - chairpersons - replacements
                
            #print chairmen, members, replacements
            retval[com_name] = (list(chairpersons),list(members),list(replacements))    
    
        return retval
    
    def convert_to_mks(self,ll):
        ll = [ int(x) for x in ll]
        ll2 = []
        for x in ll:
            try:
                ll2.append( Member.objects.get(id=x) )
            except Member.DoesNotExist:
                logger.warn("ERROR: couldn't find member for id: %s" % x)
                #raise                 
        return ll
            
    def update_committee_members_db(self,data):
        for name, details in data.iteritems():
            chairpersons, members, replacements = details
            try:
                chairpersons = self.convert_to_mks(chairpersons)
                members = self.convert_to_mks(members)
                replacements = self.convert_to_mks(replacements)
                
                cm = Committee.objects.get( name = name )
                
                cm.chairpersons.clear()
                cm.members.clear()
                cm.replacements.clear()
                
                cm.chairpersons.add(*chairpersons)
                cm.members.add(*members)
                cm.replacements.add(*replacements)
                    
            except Committee.DoesNotExist:
                logger.warn("ERROR: couldn't find committee for name: %s" % name) 
            
    def handle(self, *args, **options):
        r = self.parse_committee_members()
        logger.debug(r)
        self.update_committee_members_db(r)
    
