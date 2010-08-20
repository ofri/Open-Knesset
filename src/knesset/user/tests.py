import unittest
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from knesset.mks.models import Member

class TestFollowing(unittest.TestCase):

    def setUp(self):
        self.jacob = User.objects.create_user('jacob', 'jacob@jacobian.org',
                                              'JKM')
        self.david = Member.objects.create(name='david')
        self.yosef = Member.objects.create(name='yosef')
        self.moshe = Member.objects.create(name='moshe')

    def testFollowing(self):
        c = Client()
        p = self.jacob.get_profile()
        loggedin = c.login(username='jacob', password='JKM')
        self.assertTrue(loggedin)
        response = c.post(reverse('follow-members'), {'watch': self.david.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(p.members[0], self.david)
        response = c.post(reverse('follow-members'), {'watch': self.yosef.id})
        response = c.post(reverse('follow-members'), {'unwatch': self.david.id})
        self.assertEquals(len(p.members), 1)
        self.assertEquals(p.members[0], self.yosef)

    def tearDown(self):
        self.jacob.delete()
        self.david.delete()
        self.yosef.delete()
        self.moshe.delete()

