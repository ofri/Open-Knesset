# encoding: utf-8
import logging, re
import urllib
from datetime import datetime

from optparse import make_option
from django.core.management.base import NoArgsCommand
from bs4 import BeautifulSoup
from persons.models import Role
from mks.models import Member

logger = logging.getLogger("open-knesset.persons.update_gov_roles")

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--dont_ask', action='store_true', dest='dont_ask',
            help="always answer 'ignore' instead of asking the user. used for debugging"),
    )
    
    #TODO: scrape for the last gov
    GOVS = range(28,34)
    URI = "http://www.knesset.gov.il/govt/heb/GovtByNumber.asp?govt={}"
    
    
    def handle_noargs(self, **options):
        for i in self.GOVS:
            page = urllib.urlopen(self.URI.format(i)).read()
            bs = BeautifulSoup(page)
            table = bs.find(id="Table6")
            org = table.find("td", "Title3").text
            for j in table.find_all("tr")[7:]:
                cs = j.find_all('td')
                if len(cs) == 7:
                    if cs[1].text:
                        role = cs[1].text
                    mk_href = cs[2].find("a")['href']
                    mk_id = mk_href.split("=")[1]
                    start_date = cs[3].text.lstrip(u'מ-')[:10]
                    end_date = cs[4].text.lstrip(u'עד ')[:10]
                    person = Member.objects.get(pk=mk_id).person.all()[0]
                    # now get the field we need for the db
                    try:
                        end_date = datetime.strptime(end_date,"%d/%m/%Y")
                    except ValueError:
                        end_date = None
                        logger.warn(u"failed for parse end_date for: {} {} {}".format(
                            org, person, role))

                    r, created = Role.objects.get_or_create(person=person,
                            start_date=datetime.strptime(start_date,"%d/%m/%Y"),
                            end_date=end_date,
                            text=role,
                            org=org,
                            )
                    if created:
                        logger.info(r)
