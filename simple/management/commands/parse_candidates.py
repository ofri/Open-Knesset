#!/usr/bin/python
# coding: utf8

import urllib2
from BeautifulSoup import BeautifulSoup
import re
import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger("open-knesset.parse_candidates")

class Parties(object):

	def __init__(self, url, attr_name, attr_val):
        self.url = url
        self.attr_name = attr_name
        self.attr_val = attr_val

	def __iter__(self):
        return self

	def import_party(self, party_name, link):
		data = BeautifulSoup(urllib2.urlopen(url).read())
        ordinal = 1
		for person_name in data.find_all(attrs={"class": "candidate"}):
            try:
                person = Person.objects.get(name=person_name)
            except KeyError:
                try:
                    person = PersonAlias.objects.get(name=person_name).person
                except KeyError:
                    person = Person.objects.create(name=person_name)

            person.roles.add(start_date=datetime(2015, 1, 29),
                             org="הבחירות לכנסת ה-20",
                             text="מקום {} ב{}".format(ordinal, party_name))
            ordinal += 1

    def parse(self)
		data = BeautifulSoup(urllib2.urlopen(self.url).read())
        return imap (self.import_party,
                     data.find_all(attrs={"class": "candidates-title-k"}),
                     data.find_all(attrs={"class": "internallinkKnessetTitle"}))


class Command(BaseCommand):
    """Parse Election candidates from their webpage http://bechirot.gov.il/election/Pages/CandidatesList.aspx"""

    args = ''
    help = 'Creates persons with appropiate roles from the official election page'
    base_url = "http://bechirot.gov.il/election/Candidates/Pages/default.aspx"

    def handle(self, *args, **options):
        r = self.parse_committee_members()
        logger.debug(r)
        self.update_committee_members_db(r)

        logger.info("reading html from {}".format(self.base_url))
        parties = Parties(self.base_url)
        parties.parse()

