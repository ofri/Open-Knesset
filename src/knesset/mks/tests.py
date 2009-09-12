# encoding: utf8
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from knesset.mks.models import *

class SimpleTest(TestCase):

    def test_member_list(self):
        """ Tests member list page - number of objects = 121, and type = Member
        """
        response = self.client.get("/mks/member/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals(121, len(response.context['object_list']), "Expected to receive 121 objects, but got %d" % len(response.context['object_list']))
        self.assertEquals(Member, type( response.context['object_list'][0] ), "Expected to receive objects of type Member, but got %s" % type( response.context['object_list'][0] ))

    def test_member_detail(self):
        """ Tests member details page - for id=100 name='אופיר פינס'
        """
        response = self.client.get("/mks/member/100/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals(u'אופיר פינס-פז', response.context['object'].name, "Expected to receive some other member name")

    def test_party_list(self):
        """ Tests party list page - number of objects = 12, and type = Party
        """
        response = self.client.get("/mks/party/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals(12, len(response.context['object_list']), "Expected to receive 12 objects, but got %d" % len(response.context['object_list']))
        self.assertEquals(Party, type( response.context['object_list'][0] ), "Expected to receive objects of type Party, but got %s" % type( response.context['object_list'][0] ))

    def test_party_detail(self):
        """ Tests member details page - for id=27 name='רע"מ-תע"ל'
        """
        response = self.client.get("/mks/party/27/")
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals(u'רע"מ-תע"ל', response.context['object'].name, "Expected to receive some other party name")
    
    def test_home_page(self):
        """ Tests that the home page is present.
        """
        client = Client()
        response = client.get("/")
        self.failUnlessEqual(response.status_code, 200)
