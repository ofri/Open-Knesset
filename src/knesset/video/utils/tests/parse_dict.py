from django.test import TestCase
from knesset.video.utils.parse_dict import parse_dict, validate_dict

class testParseDict(TestCase):

    def testValidateDict(self):
        h={'id':{'$t':'test','type':'text'},'tmp':'xxx'}
        self.assertTrue(validate_dict('test','test'))
        self.assertTrue(validate_dict(h,['id','tmp']))
        self.assertTrue(validate_dict(h,{'id':['$t']}))
        self.assertTrue(validate_dict(h,{'id':{'$t':'test'}}))
        self.assertTrue(validate_dict(h,{'id':{'type':'text','$t':'test'}},['tmp']))
        self.assertFalse(validate_dict(h,['id','tmp','xxx']))
        self.assertFalse(validate_dict(h,{'id':['x']}))
        self.assertFalse(validate_dict(h,{'id':{'$t':'xxx'}}))
        self.assertFalse(validate_dict(h,{'id':{'$t':'test','type':'text2'}}))
        h={'published':None}
        self.assertFalse(validate_dict(h,['published']))
        
    def testParseDict(self):
        self.assertEqual(parse_dict('xxx','yyy'),None)
        self.assertEqual(parse_dict('xxx','yyy',default='a'),'a')
        h={'id':{'$t':'test','type':'text'},'tmp':'xxx','none':None}
        self.assertEqual(parse_dict(h,'yyy',validate=['z']),None)
        self.assertEqual(parse_dict(h,'yyy',validate=['id']),None)
        self.assertEqual(parse_dict(h,'yyy',validate=['xxx']),None)
        self.assertEqual(parse_dict(h,'tmp',validate=['id']),'xxx')
        self.assertEqual(parse_dict(h,{'id':'$t2'}),None)
        self.assertEqual(parse_dict(h,{'id':'$t'}),'test')