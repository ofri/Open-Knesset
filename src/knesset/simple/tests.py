#encoding: utf-8
import re, os, datetime

from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from knesset.simple.management.commands import parse_knesset_bill_pdf

class SyncdataTest(TestCase):

    def setUp(self):
        self.dir = os.path.abspath(os.path.join(settings.PROJECT_ROOT, os.path.pardir,os.path.pardir,'tests', ''))
        
    def test_parse_knesset_bill_pdf_text(self):
        results = parse_knesset_bill_pdf.parse_pdf_text(os.path.join(self.dir,'knesset_proposal_366.txt'), "local-testing-cache/knesset_proposal_366.txt")
        self.assertEqual(len(results), 4)
        expected_date = datetime.date(2011,2,1)
        self.assertEqual(results[0]['date'], expected_date)
        expected_title = "הצעת חוק האזרחות (תיקון מס' 10) (ביטול אזרחות בשל הרשעה בעבירה), התשע\"א1102".decode('utf8')
        self.assertEqual(results[0]['title'], expected_title)
        expected_original = u'2377/18/\u05e4'
        self.assertEqual(results[0]['original_ids'][0], expected_original)
        expected_title = "הצעת חוק הביטוח הלאומי (תיקון מס' 126) (הארכת התכנית הניסיונית), התשע\"א1102".decode('utf8')
        self.assertEqual(results[3]['title'], expected_title)
        

    def tearDown(self):
        pass
