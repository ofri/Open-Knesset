import datetime
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from actstream import action, follow
from knesset.mks.models import Member
from knesset.laws.models import Bill
from knesset.committees.models import Committee
from knesset.agendas.models import Agenda

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
                                 kwargs={'pk': self.jacob.id}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'user/public_profile.html')
        self.assertEqual(res.context['viewed_user'], self.jacob)
        res = self.client.get(reverse('public-profile',
                                 kwargs={'pk': self.adrian.id}))
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
        self.david = Member.objects.create(name='david', start_date=datetime.date(2010,1,1))

        self.yosef = Member.objects.create(name='yosef', start_date=datetime.date(2010,1,1))
        self.moshe = Member.objects.create(name='moshe', start_date=datetime.date(2010,1,1))
        self.agenda_1 = Agenda.objects.create(name='agenda_1')
        self.committee_1 = Committee.objects.create(name='c1')
        self.meeting_1 = self.committee_1.meetings.create(date=datetime.datetime.now(),
                                                         protocol_text='m1')
        self.meeting_1.create_protocol_parts()
        action.send(self.jacob, verb='farted', target=self.david)
        action.send(self.jacob, verb='hit', target=self.yosef)
        action.send(self.jacob, verb='hit', target=self.moshe)
        self.bill_1 = Bill.objects.create(stage='1', title='bill 1', popular_name="The Bill")

    def testUnfollowMeeting(self):
        follow(self.jacob, self.meeting_1)
        p = self.jacob.get_profile()
        self.assertEquals(len(p.meetings), 1)
        loggedin = self.client.login(username='jacob', password='JKM')
        self.assertTrue(loggedin)
        response = self.client.post(reverse('user-follow-unfollow'),
                                    {'what': 'meeting',
                                     'id': self.meeting_1.id,
                                     'verb':'unfollow'})
        self.assertEquals(len(p.members), 0)

    def test_following_members(self):
        """Test the following and unfollowing members using the
           generic follow method.
        """
        p = self.jacob.get_profile()
        loggedin = self.client.login(username='jacob', password='JKM')
        self.assertTrue(loggedin)
        response = self.client.post(reverse('user-follow-unfollow'),
                                    {'id': self.david.id,
                                     'what': 'member',
                                     'verb': 'follow'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(p.members[0], self.david)
        response = self.client.post(reverse('user-follow-unfollow'),
                                    {'id': self.yosef.id,
                                     'what': 'member',
                                     'verb': 'follow'})
        self.assertEquals(len(p.members), 2)
        response = self.client.post(reverse('user-follow-unfollow'),
                                    {'id': self.david.id,
                                     'what':'member',
                                     'verb':'unfollow'})
        self.assertEquals(len(p.members), 1)
        self.assertEquals(p.members[0], self.yosef)
        response = self.client.post(reverse('user-follow-unfollow'),
                                    {'id': self.yosef.id,
                                     'what': 'member',
                                     'verb': 'unfollow'})
        self.assertEquals(len(p.members), 0)
        self.client.logout()

    def test_following_bills(self):
        """Test the following and unfollowing a bill using the
           generic follow method.
        """
        p = self.jacob.get_profile()
        loggedin = self.client.login(username='jacob', password='JKM')
        self.assertTrue(loggedin)
        response = self.client.post(reverse('user-follow-unfollow'),
                                    {'id': self.bill_1.id,
                                     'what': 'bill',
                                     'verb': 'follow'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(p.bills[0], self.bill_1)
        response = self.client.post(reverse('user-follow-unfollow'),
                                    {'id': self.bill_1.id,
                                     'what': 'bill',
                                     'verb': 'unfollow'})
        self.assertEquals(len(p.bills), 0)
        self.client.logout()

    def tearDown(self):
        self.jacob.delete()
        self.david.delete()
        self.yosef.delete()
        self.moshe.delete()
        self.bill_1.delete()
        self.agenda_1.delete()
        self.committee_1.delete()
        self.meeting_1.delete()

