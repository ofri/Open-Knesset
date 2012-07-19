from django.test import TestCase
from knesset.settings import PROJECT_ROOT
from knesset.mks.models import Member
from knesset.committees.models import Committee
from knesset.mmm.models import Document, parse_json, text_lookup, verify
from datetime import datetime
import simplejson
import re

class MmmTest(TestCase):
    """ Testing mmm functions """
    
    def setUp(self):
        j = simplejson.loads(PROJECT_ROOT + "mmm/test_matches.json", 'r')
        ok_candidates = re.sub(r"\s+", r" " , " ".join(j[0]['candidates']))
        ok_date = datetime.strptime(j[0]['date'], '%d/%m/%Y')
 
    def test_parse_json(self):
        """
        Tests data modification
        """
        
        parse_json(j)
        
        
        self.assertEqual(ok_candidates, j[0]['candidates'])
        self.assertEqual(ok_date, j[0]['date'])
        
    def test_text_lookup(self):
        """
        Tests in text look up for mks and committees names
        """
        mk_name = u'\u05e8\u05d5\u05e0\u05d9\u05ea \u05ea\u05d9\u05e8\u05d5\u05e9'
        mks = Member.objects.create(name=mk_name)
        c = Committee.objects.create(name='c1')
        
        
        self.assertIn(mk_name, ok_candidates)
        
        mk = text_lookup(Member, ok_candidates)
        self.assertEqual(mks.id, mk[0])
        
        self.assertNotIn('c1', ok_candidates)
        
        committees = text_lookup(Committee, ok_candidates)
        self.assertEqual([], committees)
        
    def test_verify(self):
        """
        Tests verify method
        """
        o = j[0]
        mk_name = u'\u05e8\u05d5\u05e0\u05d9\u05ea \u05ea\u05d9\u05e8\u05d5\u05e9'
        mks = Member.objects.create(name=mk_name)
        mkses = [1]
        committees = []
        d1 = Document.objects.create(url=j[0]['url'], title=j[0]['title'], 
                                     publication_date=ok_date, author_names=j[0]['author'])
        d1.req_mks.add(mks.id)
        
        self.assertEqual(o['url'], d1.url)
        self.assertEqual(o['title'], d1.title)
        self.assertEqual(ok_date, d1.publication_date)
        self.assertEqual(o['author'], d1.author_names)
        self.assertEqual(mk_name, d1.req_mks.name)
        self.assertEqual([], d1.req_committee)
        
        self.assertTrue(verify(o, d1, mkses, committees))