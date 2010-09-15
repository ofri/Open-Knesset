from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from knesset.mks.models import Member
from actstream import action

class TestPublicProfile(TestCase):

    def setUp(self):
        self.jacob = User.objects.create_user('jacob', 'jacob@jacobian.org',
                                              'JKM')
        self.adrian = User.objects.create_user('adrian', 'adrian@example.com',
                                              'adrian')
        profile = self.adrian.get_profile()       
        profile.public_profile = False
        profile.save()
        
    def testPublicProfile(self):
        res = self.client.get(reverse('public-profile',
                                 kwargs={'object_id': self.jacob.id}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'user/public_profile.html')
        self.assertEqual(res.context['viewed_user'], self.jacob)
        res = self.client.get(reverse('public-profile',
                                 kwargs={'object_id': self.adrian.id}))
        self.assertEqual(res.status_code, 200)
        self.assertFalse('details' in res.content)


    def testProfileList(self):
        res = self.client.get(reverse('profile-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,'user/profile_list.html')
        self.assertEqual(len(res.context['object_list']), 1)

    def tearDown(self):
        self.jacob.delete()
        self.adrian.delete()

class TestFollowing(TestCase):

    def setUp(self):
        self.jacob = User.objects.create_user('jacob', 'jacob@jacobian.org',
                                              'JKM')
        self.david = Member.objects.create(name='david')
        self.yosef = Member.objects.create(name='yosef')
        self.moshe = Member.objects.create(name='moshe')
        action.send(self.jacob, verb='farted', target=self.david)
        action.send(self.jacob, verb='hit', target=self.yosef)
        action.send(self.jacob, verb='hit', target=self.moshe)
        

    def testFollowing(self):
        p = self.jacob.get_profile()
        loggedin = self.client.login(username='jacob', password='JKM')
        self.assertTrue(loggedin)
        response = self.client.post(reverse('follow-members'), {'watch': self.david.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(p.members[0], self.david)
        response = self.client.post(reverse('follow-members'), {'watch': self.yosef.id})
        response = self.client.post(reverse('follow-members'), {'unwatch': self.david.id})
        self.assertEquals(len(p.members), 1)
        self.assertEquals(p.members[0], self.yosef)
        self.client.logout()

    def tearDown(self):
        self.jacob.delete()
        self.david.delete()
        self.yosef.delete()
        self.moshe.delete()

