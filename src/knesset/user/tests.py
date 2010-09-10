from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from knesset.mks.models import Member
from actstream import action

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

    def testPublicProfile(self):
        res = self.client.get(reverse('public-profile',
                                 kwargs={'object_id': self.jacob.id}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'user/public_profile.html')
        #actions = res.context['aggr_actions']
        #actions_list = map(lambda x: (x.verb, x.targets.keys()), actions)
        #actions_list.sort()
        #self.assertEqual(actions_list,
        #                 [('farted', [self.david]), ('hit', [self.yosef,self.moshe])])

    def tearDown(self):
        self.jacob.delete()
        self.david.delete()
        self.yosef.delete()
        self.moshe.delete()

