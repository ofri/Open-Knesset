from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser
from knesset.mks.models import Member, Party, Membership
from knesset.mks.views import MemberListView
from knesset.utils import RequestFactory

just_id = lambda x: x.id

class MemberViewsTest(TestCase):

    def setUp(self):
        self.party_1 = Party.objects.create(name='party 1')
        self.party_2 = Party.objects.create(name='party 2')
        self.mk_1 = Member.objects.create(name='mk_1',
                                           current_party=self.party_1)
        self.mk_2 = Member.objects.create(name='mk_2',
                                           current_party=self.party_1)
        self.jacob = User.objects.create_user('jacob', 'jacob@jacobian.org',
                                              'JKM')

    def testMemberList(self):
        res = self.client.get(reverse('member-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'mks/member_list_with_bars.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.mk_1.id, self.mk_2.id, ])

    def testMemberDetail(self):
        res = self.client.get(reverse('member-detail', 
                                      kwargs={'object_id': self.mk_1.id}))
        self.assertTemplateUsed(res,
                                'mks/member_detail.html')
        self.assertEqual(res.context['object'].id, self.mk_1.id)

    def testPartyList(self):
        res = self.client.get(reverse('party-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'mks/party_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.party_1.id, self.party_2.id, ])

    def testPartyDetail(self):
        res = self.client.get(reverse('party-detail', 
                              kwargs={'object_id': self.party_1.id}))
        self.assertTemplateUsed(res, 'mks/party_detail.html')
        self.assertEqual(res.context['object'].id, self.party_1.id)

    def testMemberDetailsContext(self):

        # test anonymous user
        mk_1_url = self.mk_1.get_absolute_url()
        res = self.client.get(mk_1_url)
        self.assertFalse(res.context['watched_member'])
        # test autherized user
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.get(mk_1_url)
        self.assertFalse(res.context['watched_member'])
        # test autherized user that follows
        p = self.jacob.get_profile()
        p.followed_members.add(self.mk_1)
        res = self.client.get(mk_1_url)
        self.assertTrue(res.context['watched_member'])

    def tearDown(self):
        self.party_1.delete()
        self.party_2.delete()
        self.mk_1.delete()
        self.mk_2.delete()
        self.jacob.delete()

