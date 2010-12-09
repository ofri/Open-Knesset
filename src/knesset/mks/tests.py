from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from actstream import follow,action
from actstream.models import Action
from knesset.mks.models import Member, Party, Membership
from knesset.mks.views import MemberListView
from knesset.laws.models import Law,Bill,PrivateProposal,Vote,VoteAction
from knesset.committees.models import CommitteeMeeting,Committee
from knesset.utils import RequestFactory
import datetime
import feedparser
from backlinks.client  import BacklinksClient
just_id = lambda x: x.id

class MemberViewsTest(TestCase):

    def setUp(self):
        self.party_1 = Party.objects.create(name='party 1')
        self.party_2 = Party.objects.create(name='party 2')
        self.mk_1 = Member.objects.create(name='mk_1',
                                          start_date=datetime.date(2010,1,1),
                                          current_party=self.party_1)
        self.mk_2 = Member.objects.create(name='mk_2',
                                          start_date=datetime.date(2010,1,1),
                                           current_party=self.party_1)
        self.jacob = User.objects.create_user('jacob', 'jacob@jacobian.org',
                                              'JKM')

        self.committee_1 = Committee.objects.create(name='c1')
        self.meeting_1 = self.committee_1.meetings.create(date=datetime.date.today()-datetime.timedelta(1),
                                 protocol_text='jacob:\nI am a perfectionist\nadrian:\nI have a deadline')
        self.meeting_2 = self.committee_1.meetings.create(date=datetime.date.today()-datetime.timedelta(2),
                                 protocol_text='adrian:\nYou are a perfectionist\njacob:\nYou have a deadline')
        self.law = Law.objects.create(title='law 1')
        self.pp = PrivateProposal.objects.create(title='private proposal 1', date=datetime.date.today()-datetime.timedelta(3))
        self.pp.proposers.add(self.mk_1)
        self.bill_1 = Bill.objects.create(stage='1', title='bill 1', law=self.law)
        self.bill_1.proposals.add(self.pp)
        self.bill_1.proposers.add(self.mk_1)
        self.meeting_1.mks_attended.add(self.mk_1)
        self.meeting_1.save()
        self.meeting_2.mks_attended.add(self.mk_1)
        self.meeting_2.save()
        self.vote = Vote.objects.create(title='vote 1',time=datetime.datetime.now())
        self.vote_action = VoteAction.objects.create(member=self.mk_1, vote=self.vote, type='for')

        self.domain = 'http://' + Site.objects.get_current().domain

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

    def testMemberSearch(self):
        import json

        res = self.client.get(reverse('member-handler'),
                                      {'q': 'mk_'},
                                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        p = json.loads(res.content)
        self.assertEqual(set(map(lambda x: x['id'], p)), set((self.mk_1.id, self.mk_2.id)))

        res = self.client.get(reverse('member-handler'),
                                      {'q': 'mk_1'},
                                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        p = json.loads(res.content)
        self.assertEqual(map(lambda x:x['id'], p), [self.mk_1.id])

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

    def testPartySearch(self):
        import json

        res = self.client.get(reverse('party-handler'),
                                      {'q': 'party'},
                                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        p = json.loads(res.content)
        self.assertEqual(set(map(lambda x: x['id'], p)), set((self.party_1.id,self.party_2.id)))

        res = self.client.get(reverse('party-handler'),
                                      {'q': 'party%201'},
                                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        p = json.loads(res.content)
        self.assertEqual(map(lambda x:x['id'], p), [self.party_1.id])

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
        follow(self.jacob, self.mk_1)
        res = self.client.get(mk_1_url)
        self.assertTrue(res.context['watched_member'])

    def testMemberActivityFeed(self):
        res = self.client.get(reverse('member-activity-feed', 
                                      kwargs={'object_id': self.mk_1.id}))
        self.assertEqual(res.status_code,200)
        parsed = feedparser.parse(res.content)
        self.assertEqual(len(parsed['entries']),4)
        self.assertEqual(parsed['entries'][3]['link'], self.domain + self.bill_1.get_absolute_url())
        self.assertEqual(parsed['entries'][2]['link'], self.domain + self.meeting_2.get_absolute_url())
        self.assertEqual(parsed['entries'][1]['link'], self.domain + self.meeting_1.get_absolute_url())        
        self.assertEqual(parsed['entries'][0]['link'], self.domain + self.vote.get_absolute_url())
        

    def testMemberActivityFeedWithVerbProposed(self):
        res = self.client.get(reverse('member-activity-feed', 
                                      kwargs={'object_id': self.mk_1.id}),{'verbs':'proposed'})
        self.assertEqual(res.status_code,200)
        parsed = feedparser.parse(res.content)
        self.assertEqual(len(parsed['entries']),1)

        res = self.client.get(reverse('member-activity-feed', 
                                      kwargs={'object_id': self.mk_2.id}),{'verbs':'proposed'})
        self.assertEqual(res.status_code,200)
        parsed = feedparser.parse(res.content)
        self.assertEqual(len(parsed['entries']),0)


    def testMemberActivityFeedWithVerbAttended(self):
        res = self.client.get(reverse('member-activity-feed', 
                                      kwargs={'object_id': self.mk_1.id}),{'verbs':'attended'})
        self.assertEqual(res.status_code,200)
        parsed = feedparser.parse(res.content)
        self.assertEqual(len(parsed['entries']),2)

        res = self.client.get(reverse('member-activity-feed', 
                                      kwargs={'object_id': self.mk_2.id}),{'verbs':'attended'})
        self.assertEqual(res.status_code,200)
        parsed = feedparser.parse(res.content)
        self.assertEqual(len(parsed['entries']),0)


    def testMemberActivityFeedWithVerbJoined(self):
        res = self.client.get(reverse('member-activity-feed', 
                                      kwargs={'object_id': self.mk_1.id}),{'verbs':'joined'})
        self.assertEqual(res.status_code,200)
        parsed = feedparser.parse(res.content)
        self.assertEqual(len(parsed['entries']),0)


    def testMemberActivityFeedWithVerbPosted(self):
        res = self.client.get(reverse('member-activity-feed', 
                                      kwargs={'object_id': self.mk_1.id}),{'verbs':'posted'})
        self.assertEqual(res.status_code,200)
        parsed = feedparser.parse(res.content)
        self.assertEqual(len(parsed['entries']),0)
        
    def testPingbacks(self):
        

        
    def tearDown(self):
        self.party_1.delete()
        self.party_2.delete()
        self.mk_1.delete()
        self.mk_2.delete()
        self.jacob.delete()

