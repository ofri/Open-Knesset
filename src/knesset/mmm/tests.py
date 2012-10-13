# -*- coding: utf-8 -*-
from datetime import datetime

from django.test import TestCase
from django.utils import simplejson
from knesset.mmm.fuzzy_match import fuzzy_match

from knesset.settings import PROJECT_ROOT
from knesset.mks.models import Member
from knesset.committees.models import Committee
from knesset.mmm.models import Document, text_lookup, verify
from knesset.mmm.management.commands.update_mmm import parse_json, combine_jsons


matches = PROJECT_ROOT + "/mmm/test_matches.json"
mmm =  PROJECT_ROOT + "/mmm/test_mmm.json"

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

    def test_fuzzy_match(self):
        name = u'הוועדה לקידום מעמד האישה'
        text = u'מוגש ועדה לקידו4 מעמד האישה'

        self.assertTrue(fuzzy_match(name, text))

    def test_text_lookup(self):
        m1 = Member.objects.create(name=u'משה בינת')
        m2 = Member.objects.create(name=u'בני')
        text = u'מסמך זה נכתב בשביל משה בינת'
        text_fuzzy = u'מסמך זה נכתב לבקשת משה בינט, חבר כנסת'

        self.assertTrue(m1.name in text)
        self.assertEqual(1, len(text_lookup(Member, text)))
        self.assertEqual(1, len(text_lookup(Member, text_fuzzy)))

    def test_vairfy(self):
        match = {
            "docid": "m02254",
            "title": u"\u05ea\u05d9\u05e2\u05d5\u05d3 \u05d7\u05d6\u05d5\u05ea\u05d9 \u05d5\u05e7\u05d5\u05dc\u05d9 \u05e9\u05dc \u05d7\u05e7\u05d9\u05e8\u05ea \u05d7\u05e9\u05d5\u05d3\u05d9\u05dd",
            "url": u"http://knesset.gov.il/mmm/data/pdf/m02254.pdf",
            "entityName": u"\u05d5\u05e2\u05d3\u05ea \u05d4\u05d7\u05d5\u05e7\u05d4 \u05d7\u05d5\u05e7 \u05d5\u05de\u05e9\u05e4\u05d8",
            "heading": u"\u05de\u05e1\u05de\u05da \u05d6\u05d4 \u05e0\u05db\u05ea\u05d1 \u05dc\u05e7\u05e8\u05d0\u05ea \u05d3\u05d9\u05d5\u05df \u05d5\u05e2\u05d3\u05ea \u05d4\u05d7\u05d5\u05e7\u05d4 \u05d7\u05d5\u05e7 \u05d5\u05de\u05e9\u05e4\u05d8 \u05e9\u05dc \u05d4\u05db\u05e0\u05e1\u05ea \u05d1\u05e1\u05e2\u05d9\u05e3 23 \u05dc\u05d4\u05e6\u05e2\u05ea \u05d7\u05d5\u05e7 \u05d4\u05d4\u05ea\u05d9\u05d9\u05e2\u05dc\u05d5\u05ea \u05d4\u05db\u05dc\u05db\u05dc\u05d9\u05ea \u05ea\u05d9\u05e7\u05d5\u05e0\u05d9 \u05d7\u05e7\u05d9\u05e7\u05d4 \u05dc\u05d9\u05d9\u05e9\u05d5\u05dd \u05d4\u05ea\u05d5\u05db\u05e0\u05d9\u05ea \u05d4\u05db\u05dc\u05db\u05dc\u05d9\u05ea \u05dc\u05e9\u05e0\u05d9\u05dd 9002 \u05d5 0102 \u05d4\u05ea\u05e9\u05e1\u05d8 90021 \u05dc\u05d4\u05dc\u05df \u05d4\u05e6\u05e2\u05ea \u05d4\u05d7\u05d5\u05e7",
            "score": 100,
            "date": "2/7/2009",
            "id": 10005,
            "author": u"\u05d3\u05d9\u05e0\u05d4  \u05e6\u05d3\u05d5\u05e7"
        }

        match['date'] = datetime.strptime(match['date'], '%d/%m/%Y').date()

        mmm_doc = Document.objects.create(
            url = match['url'],
            title = match['title'],
            publication_date = match['date'],
            author_names = match['author'],
        )


        m = Member.objects.create(name='name')
        m2 = Member.objects.create(name='name1')
        mks = [m.id, m2.id]
        committees = []
        mmm_doc.req_mks = mks

        self.assertEqual(mks, list(mmm_doc.req_mks.values_list('pk', flat=True)))
        doc = Document.objects.get(url=match['url'])

#        self.assertTrue(verify(match, i, mks, committees))
        m3 = Member.objects.create(name='name3')
        m4 = Member.objects.create(name='name4')
        mks2 = [m3.id, m4.id]
        self.assertNotEqual(mks2, list(doc.req_mks.values_list('pk', flat=True)))
        self.assertTrue(verify(match, doc, mks2, committees))