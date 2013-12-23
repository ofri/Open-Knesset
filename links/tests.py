import unittest
import re
import os
import datetime
from django.conf import settings
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.sites.models import Site
from django.template import Template, Context
from links.models import Link, LinkType, ModelWithLinks
from mks.models import Member, Knesset

class TestViews(unittest.TestCase):

    def setUp(self):
        self.type_a = LinkType.objects.create(title='a')
        self.obj = Site.objects.create(domain="example.com", name="example")
        self.l1 = Link.objects.create(url='http://www.example.com/l1', title='l1',
                                 content_object=self.obj, link_type=self.type_a)
        # make sure
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, 'icons' , 'testimage.png'))
        except OSError:
            pass

    def testTextType(self):
        # test a link with no image type
        self.type_a.image = None
        self.type_a.save()
        c = Context ({'obj': self.obj})
        t = Template('{% load links_tags %}{% object_links obj %}')
        r = re.sub('\s', '', t.render(c))
        self.assertEquals(r,
    '<li>&nbsp;(a)<ahref="http://www.example.com/l1"target="_blank">l1</a></li>')

    def testImageType(self):
        # test a link with  a type image
        f = open(os.path.join(settings.PROJECT_ROOT, "testdata", "testimage.png"),"r")
        self.type_a.image=File(f)
        self.type_a.save()
        c = Context ({'obj': self.obj})
        t = Template('{% load links_tags %}{% object_links obj %}')
        r = re.sub('\s', '', t.render(c))
        self.assertEquals(
            r,
            '<li>&nbsp;<imgsrc="' +
            settings.MEDIA_URL +
            'icons/testimage.png"alt="a"><ahref="http://www.example.com/l1"target="_blank">l1</a></li>')

    def tearDown(self):
        self.l1.delete()
        self.type_a.delete()
        self.obj.delete()

# from django.test import TestCase
class TestModels(unittest.TestCase):

    def setUp(self):
        self.knesset = Knesset.objects.create(
            number=1,
            start_date=datetime.date.today() - datetime.timedelta(10))
        self.default_link = LinkType.objects.create(title='default')
        self.mk = Member.objects.create(name='MK')
        self.link = Link.objects.create(url='http://www.google.com/', title='google', content_object=self.mk)

    def testLink(self):
        self.assertEqual(self.link.link_type, self.default_link)
        self.assertEqual(self.link.__unicode__(), u'google: http://www.google.com/')

    def tearDown(self):
        self.knesset.delete()
        self.default_link.delete()
        self.mk.delete()
        self.link.delete()
