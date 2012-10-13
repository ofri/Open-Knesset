from django.test import TestCase
from knesset.settings import PROJECT_ROOT
from knesset.mks.models import Member
from knesset.committees.models import Committee
from knesset.mmm.models import Document, text_lookup, verify
from knesset.mmm.management.commands.update_mmm import parse_json, combine_jsons
from datetime import datetime
import simplejson


matches = PROJECT_ROOT + "/mmm/test_matches.json"
mmm =  PROJECT_ROOT + "/mmm/test_mmm.json"
JSON = simplejson.load(open(matches, 'rt'))
MMM = simplejson.load(open(mmm, 'rt'))
OK_CANDIDATES = JSON[0]['entityName']
OK_DATE = datetime.strptime(JSON[0]['date'], '%d/%m/%Y')

class MmmTest(TestCase):
    """ Testing mmm functions """

    def test_parse_json(self):
        """
        Tests data modification
        """

        j = parse_json(open(matches).read())

        for o in j:
            self.assertTrue(type(o['date'] is datetime.date))

    def test_combine_jsons(self):
        json1 = open(mmm, 'rt').read()
        json2 = open(matches, 'rt').read()
        j = combine_jsons(json2, json1)

        self.assertTrue(isinstance(j[0]['author'], basestring))

    def test_text_lookup(self):
