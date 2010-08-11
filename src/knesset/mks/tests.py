from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser
from knesset.mks.models import Member, Party, Membership
from knesset.mks.views import MemberListView
from knesset.utils import RequestFactory

class TestFollowers(TestCase):

    def setUp(self):
        self.jacob = User.objects.create_user('jacob', 'jacob@jacobian.org',
                                              'JKM')
        self.david = Member.objects.create(name='david')
        self.member_list_view = MemberListView(queryset = Member.objects.all())

    def testMemberDetailsContext(self):

        # test anonymous user
        rf = RequestFactory()
        anon = AnonymousUser()
        request = rf.get('/')
        request.user = anon
        context = self.member_list_view.get_object_context(request, self.david.id)
        self.assertFalse(context['watched_member'])
        # test autherized user
        request.user = self.jacob
        context = self.member_list_view.get_object_context(request, self.david.id)
        self.assertFalse(context['watched_member'])
        # test autherized user that follows
        p = self.jacob.get_profile()
        p.followed_members.add(self.david)
        context = self.member_list_view.get_object_context(request, self.david.id)
        self.assertTrue(context['watched_member'])

    def tearDown(self):
        self.jacob.delete()
        self.david.delete()

just_id = lambda x: x.id

class MemberViewsTest(TestCase):

    def setUp(self):
        self.party_1 = Party.objects.create(name='party 1')
        self.party_2 = Party.objects.create(name='party 2')
        self.david = Member.objects.create(name='david',
                                           current_party=self.party_1)
        self.menny = Member.objects.create(name='menny',
                                           current_party=self.party_1)

    def testMemberList(self):
        res = self.client.get(reverse('member-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'mks/member_list_with_bars.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.david.id, self.menny.id, ])

    def testMemberDetail(self):
        res = self.client.get(reverse('member-detail', 
                                      kwargs={'object_id': self.david.id}))
        self.assertTemplateUsed(res,
                                'mks/member_detail.html')
        self.assertEqual(res.context['object'].id, self.david.id)

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

    def tearDown(self):
        self.party_1.delete()
        self.party_2.delete()
        self.david.delete()
        self.menny.delete()

