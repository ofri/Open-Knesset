from datetime import datetime
from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from knesset.laws.models import Bill
from knesset.mks.models import Member
from models import *

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("Need a json decoder")

just_id = lambda x: x.id

class BillViewsTest(TestCase):

    def setUp(self):
        self.vote_1 = Vote.objects.create(time=datetime.now(),
                                          title='vote 1')
        self.vote_2 = Vote.objects.create(time=datetime.now(), 
                                          title='vote 2')
        self.jacob = User.objects.create_user('jacob', 'jacob@example.com',
                                              'JKM')
        self.bill_1 = Bill.objects.create(stage='1', title='bill 1')
        self.bill_2 = Bill.objects.create(stage='2', title='bill 2')
        self.kp_1 = KnessetProposal.objects.create(booklet_number=2, bill=self.bill_1)
        self.mk_1 = Member.objects.create(name='mk 1')

    def testBillList(self):
        res = self.client.get(reverse('bill-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'laws/bill_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.bill_1.id, self.bill_2.id, ])
    def testBillListByStage(self):
        res = self.client.get(reverse('bill-list'), {'stage': 'all'})
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.bill_1.id, self.bill_2.id, ])
        res = self.client.get(reverse('bill-list'), {'stage': '1'})
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), [self.bill_1.id])
        res = self.client.get(reverse('bill-list'), {'stage': '2'})
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), [self.bill_2.id])

    def testBillListByBooklet(self):
        res = self.client.get(reverse('bill-list'), {'booklet': '2'})
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), [self.bill_1.id])

    def testBillDetail(self):
        res = self.client.get(reverse('bill-detail',
                                 kwargs={'object_id': self.bill_1.id}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'laws/bill_detail.html')
        self.assertEqual(res.context['object'].id, self.bill_1.id)

    def testLoginRequired(self):
        res = self.client.post(reverse('bill-detail',
                           kwargs={'object_id': self.bill_1.id}))
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res['location'].startswith('%s%s'  %
                                       ('http://testserver', settings.LOGIN_URL)))

    def testPOSTApprovalVote(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.post(reverse('bill-detail',
                           kwargs={'object_id': self.bill_1.id}),
                               {'user_input_type': 'approval vote',
                                'vote_id': self.vote_1.id})
        self.assertEqual(res.status_code, 302)
        self.bill_1 = Bill.objects.get(pk=self.bill_1.id)
        self.assertEqual(self.bill_1.approval_vote, self.vote_1)
        self.assertEqual(self.bill_1.first_vote, None)
        self.assertFalse(self.bill_1.pre_votes.all())
        # cleanup
        self.bill_1.approval_vote = None
        self.bill_1.save()
        self.client.logout()

    def testPOSTFirstVote(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.post(reverse('bill-detail',
                           kwargs={'object_id': self.bill_1.id}),
                               {'user_input_type': 'first vote',
                                'vote_id': self.vote_2.id})
        self.assertEqual(res.status_code, 302)
        self.bill_1 = Bill.objects.get(pk=self.bill_1.id)
        self.assertEqual(self.bill_1.first_vote, self.vote_2)
        self.assertEqual(self.bill_1.approval_vote, None)
        self.assertFalse(self.bill_1.pre_votes.all())
        # cleanup
        self.bill_1.first_vote = None
        self.bill_1.save()
        self.client.logout()

    def testPOSTPreVote(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.post(reverse('bill-detail',
                           kwargs={'object_id': self.bill_1.id}),
                               {'user_input_type': 'pre vote',
                                'vote_id': self.vote_2.id})
        self.assertEqual(res.status_code, 302)
        self.bill_1 = Bill.objects.get(pk=self.bill_1.id)
        self.assertTrue(self.vote_2 in self.bill_1.pre_votes.all())
        self.assertEqual(self.bill_1.first_vote, None)
        self.assertEqual(self.bill_1.approval_vote, None)
        # cleanup
        self.bill_1.pre_votes.clear()
        self.client.logout()
        self.client.logout()

    def tearDown(self):
        self.vote_1.delete()
        self.vote_2.delete()
        self.bill_1.delete()
        self.bill_2.delete()
        self.jacob.delete()
        self.mk_1.delete()

class VoteViewsTest(TestCase):

    def setUp(self):
        self.vote_1 = Vote.objects.create(time=datetime(2001, 9, 11),
                                          title='vote 1')
        self.vote_2 = Vote.objects.create(time=datetime.now(), 
                                          title='vote 2')

    def testVoteList(self):
        res = self.client.get(reverse('vote-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'laws/vote_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.vote_2.id, self.vote_1.id, ])

    def testVoteDetail(self):
        res = self.client.get(reverse('vote-detail',
                                 kwargs={'object_id': self.vote_1.id}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'laws/vote_detail.html')
        self.assertEqual(res.context['object'].id, self.vote_1.id)

    def tearDown(self):
        self.vote_1.delete()
        self.vote_2.delete()

class testVoteAPI(TestCase):
    def setUp(self):
        self.vote_1 = Vote.objects.create(time=datetime(2001, 9, 11),
                                          title='vote 1')
        self.vote_2 = Vote.objects.create(time=datetime.now(), 
                                          title='vote 2')

    def testDaysBackAPI(self):
        res = self.client.get(reverse('vote-handler'), {'days_back': '300'}) 
        self.assertEqual(res.status_code,200)
        votes = json.loads(res.content)
        self.assertEqual(map(lambda x: x['title'], votes), [self.vote_2.title])
        res = self.client.get(reverse('vote-handler'), {'days_back': '30000'}) 
        self.assertEqual(res.status_code,200)
        votes = json.loads(res.content)
        self.assertEqual(set(map(lambda x: x['title'], votes)), set([self.vote_1.title, self.vote_2.title]))
    
    def tearDown(self):
        self.vote_1.delete()
        self.vote_2.delete()
# TODO: add testing for suggest_tag, vote_on_tag and tagged-votes views
