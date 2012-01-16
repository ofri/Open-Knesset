#encoding: utf-8

from youtube import testYoutube
from parse_dict import testParseDict
from mms import testMms

from django.test import TestCase
import collections
from knesset.video.utils import build_url, get_videos_queryset
from knesset.mks.models import Member
from knesset.video.models import Video

class TestUtils(TestCase):

    def testBuildUrl(self):
        url='base'
        q=collections.OrderedDict([('id',12345),('none',None),('str','string'),('uni',u'בדיקה')])
        self.assertEqual(build_url(url,q),'base?id=12345&none=&str=string&uni=%D7%91%D7%93%D7%99%D7%A7%D7%94')
