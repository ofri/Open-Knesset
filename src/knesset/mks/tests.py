import unittest
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser
from knesset.mks.models import Member
from knesset.mks.views import MemberListView

class TestViews(unittest.TestCase):

    def setUp(self):
        self.jacob = User.objects.create_user('jacob', 'jacob@jacobian.org',
                                              'JKM')
        self.david = Member.objects.create(name='david')
        self.member_list_view = MemberListView(queryset = Member.objects.all())

    def testMemberDetailsContext(self):

        # test anonymous user
        anon = AnonymousUser()
        context = self.member_list_view.get_object_context(anon, self.david.id)
        self.assertFalse(context['watched_member'])
        # test autherized user
        context = self.member_list_view.get_object_context(self.jacob, self.david.id)
        self.assertFalse(context['watched_member'])
        # test autherized user that follows
        p = self.jacob.get_profile()
        p.followed_members.add(self.david)
        context = self.member_list_view.get_object_context(self.jacob, self.david.id)
        self.assertTrue(context['watched_member'])

    def tearDown(self):
        self.jacob.delete()
        self.david.delete()
