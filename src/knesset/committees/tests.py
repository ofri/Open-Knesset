from datetime import datetime
from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from knesset.laws.models import Bill
from knesset.mks.models import Member
from models import *

just_id = lambda x: x.id

class ListViewTest(TestCase):

    def setUp(self):
        self.committee_1 = Committee.objects.create(name='c1')
        self.committee_2 = Committee.objects.create(name='c2')
        self.meeting_1 = self.committee_1.meetings.create(date=datetime.now(),
                                                         protocol_text='m1')
        self.meeting_2 = self.committee_1.meetings.create(date=datetime.now(),
                                                         protocol_text='m2')
        self.jacob = User.objects.create_user('jacob', 'jacob@example.com',
                                              'JKM')
        self.bill_1 = Bill.objects.create(stage='1', title='bill 1')
        self.mk_1 = Member.objects.create(name='mk 1')

    def testCommitteeList(self):
        res = self.client.get(reverse('committee-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'committees/committee_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.committee_1.id, self.committee_2.id, ])

    def testCommitteeMeetings(self):
        res = self.client.get(reverse('committee-detail',
                                 kwargs={'committee_id': self.committee_1.id}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'committees/committeemeeting_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [self.meeting_1.id, self.meeting_2.id, ], 
                         'object_list has wrong objects: %s' % object_list)

    def testLoginRequired(self):
        res = self.client.post(reverse('committee-meeting',
                           kwargs={'object_id': self.meeting_1.id}))
        self.assertFalse(self.bill_1 in self.meeting_1.bills_first.all())
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res['location'].startswith('http://testserver/user/login/'))

    def testConnectToMK(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.post(reverse('committee-meeting',
                           kwargs={'object_id': self.meeting_1.id}),
                               {'user_input_type': 'mk',
                                'mk_name': self.mk_1.name})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(self.meeting_1 in self.mk_1.committee_meetings.all())
        self.client.logout()

    def testConnectToBill(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.post(reverse('committee-meeting',
                                       kwargs={'object_id':
                                               self.meeting_1.id}),
                               {'user_input_type': 'bill',
                                'bill_id': self.bill_1.id})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(self.bill_1 in self.meeting_1.bills_first.all())
        self.client.logout()

    def tearDown(self):
        self.meeting_1.delete()
        self.meeting_2.delete()
        self.committee_1.delete()
        self.committee_2.delete()
        self.jacob.delete()
        self.bill_1.delete()
        self.mk_1.delete()

