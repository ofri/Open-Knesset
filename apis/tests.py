import datetime, json, csv
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission
from tagging.models import Tag, TaggedItem
from laws.models import Vote, VoteAction, Bill, Law
from mks.models import Member, Party, Knesset
from agendas.models import Agenda
from committees.models import Committee
from events.models import Event
from django.core import cache
from voting.models import Vote as UserVote
import apis

class TestAPIV2(TestCase):
    """
    General tests for the API V2, not specific to any app (app-specific tests
    are located in the app directories).
    """

    def setUp(self):
        pass

    def test_empty_cache_bug(self):
        """ Tastypie has a bug when the cache returns None. this test verifies
        that our fork of Tastypie doesn't have it. This test should be run with
        DummyCache settings"""
        res = self.client.get('/api/v2/vote/?format=json')
        self.assertEqual(res.status_code, 200)


class MeetingApiTest(TestCase):

    def setUp(self):
        self.knesset = Knesset.objects.create(number=1,
                            start_date=datetime.date.today()-datetime.timedelta(days=1))
        self.committee_1 = Committee.objects.create(name='c1')
        self.committee_2 = Committee.objects.create(name='c2')
        self.meeting_1 = self.committee_1.meetings.create(date=datetime.datetime.now(),
                                 protocol_text='''jacob:
I am a perfectionist
adrian:
I have a deadline''')
        self.meeting_1.create_protocol_parts()
        self.meeting_2 = self.committee_1.meetings.create(date=datetime.datetime.now(),
                                                         protocol_text='m2')
        self.meeting_2.create_protocol_parts()
        self.jacob = User.objects.create_user('jacob', 'jacob@example.com',
                                              'JKM')
        self.adrian = User.objects.create_user('adrian', 'adrian@example.com',
                                              'ADRIAN')
        (self.group, created) = Group.objects.get_or_create(name='Valid Email')
        if created:
            self.group.save()
        self.group.permissions.add(Permission.objects.get(name='Can add annotation'))
        self.jacob.groups.add(self.group)

        ct = ContentType.objects.get_for_model(Tag)
        self.adrian.user_permissions.add(Permission.objects.get(codename='add_tag', content_type=ct))

        self.bill_1 = Bill.objects.create(stage='1', title='bill 1')
        self.mk_1 = Member.objects.create(name='mk 1')
        self.topic = self.committee_1.topic_set.create(creator=self.jacob,
                                                title="hello", description="hello world")
        self.tag_1 = Tag.objects.create(name='tag1')

    def testCommitteeMeetingV2(self):
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'committeemeeting', 'api_name': 'v2'})
        url = url + str(self.meeting_1.id) + '/?format=json'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        res_json = json.loads(res.content)
        committee_url = reverse('api_dispatch_list', kwargs={'resource_name': 'committee', 'api_name': 'v2'})
        committee_url = committee_url + str(self.committee_1.id) + '/'
        self.assertEqual(res_json['committee'], committee_url)
        self.assertEqual(res_json['absolute_url'], self.meeting_1.get_absolute_url())

    def testCommitteeMeetingListV2(self):
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'committeemeeting', 'api_name': 'v2'})
        url = url + '?format=json'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        res_json = json.loads(res.content)
        self.assertEqual(len(res_json['objects']), 2)
        self.assertTrue(
            res_json['objects'][0]['absolute_url'] == self.meeting_1.get_absolute_url()
            or
            res_json['objects'][0]['absolute_url'] == self.meeting_2.get_absolute_url()
        )

    def testCommitteeMeetingV2CSV(self):
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'committeemeeting', 'api_name': 'v2'})
        url = url + '?format=csv'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        for row in csv.DictReader(res.content.split('\n'), delimiter=','):
            if row.has_key('absolute_url'):
                absurl = row['absolute_url']
            else:
                # \ufeff is the BOM - which is required for excel compatibility
                absurl = row[u'\ufeff'.encode('utf8')+'absolute_url']
                self.assertTrue(
                    absurl == self.meeting_1.get_absolute_url()
                    or
                    absurl == self.meeting_2.get_absolute_url()
                )


class SwaggerTest(TestCase):
    def testSwaggerUI(self):
        "Swagger UI static resources should be properly mounted and served"
        res = self.client.get(reverse('tastypie_swagger:index'))
        self.assertEqual(res.status_code, 200)
        self.assertIn("<title>Swagger UI</title>", res.content)

    def testSwaggerResources(self):
        "Swagger should find all the apis and list them as resources"
        res = self.client.get(reverse('tastypie_swagger:resources'))
        self.assertEqual(res.status_code, 200)
        res_json = json.loads(res.content)
        self.assertEqual(res_json["swaggerVersion"], "1.1")
        rendered_apis = [api_obj_path['path'].lstrip('/') for api_obj_path in res_json["apis"]]
        for api in apis.resources.v2_api._canonicals:
            self.assertIn(api, rendered_apis)

    def testSwaggerSchema(self):
        "The schema for swagger should be generated properly for at least one controller"
        res = self.client.get('/api/v2/doc/schema/agenda/')
        self.assertEqual(res.status_code, 200)
        res_json = json.loads(res.content)
        self.assertEqual(res_json["swaggerVersion"], "1.1")
