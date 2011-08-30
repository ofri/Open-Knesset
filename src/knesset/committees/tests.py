from datetime import datetime
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User,Group,Permission
from django.contrib.contenttypes.models import ContentType
from annotatetext.models import Annotation
from actstream.models import Action
from knesset.laws.models import Bill
from knesset.mks.models import Member
from knesset.topics.models import Topic
from models import *

just_id = lambda x: x.id

class ListViewTest(TestCase):

    def setUp(self):
        self.committee_1 = Committee.objects.create(name='c1')
        self.committee_2 = Committee.objects.create(name='c2')
        self.meeting_1 = self.committee_1.meetings.create(date=datetime.now(),
                                 protocol_text='''jacob:
I am a perfectionist
adrian:
I have a deadline''')
        self.meeting_1.create_protocol_parts()
        self.meeting_2 = self.committee_1.meetings.create(date=datetime.now(),
                                                         protocol_text='m2')
        self.meeting_2.create_protocol_parts()
        self.jacob = User.objects.create_user('jacob', 'jacob@example.com',
                                              'JKM')
        (self.group, created) = Group.objects.get_or_create(name='Valid Email')
        if created:
            self.group.save()
        self.group.permissions.add(Permission.objects.get(name='Can add annotation'))
        self.jacob.groups.add(self.group)
        self.bill_1 = Bill.objects.create(stage='1', title='bill 1')
        self.mk_1 = Member.objects.create(name='mk 1')

    def testProtocolPart(self):
        parts_list = self.meeting_1.parts.list()
        self.assertEqual(parts_list.count(), 2)
        self.assertEqual(parts_list[0].header, u'jacob')
        self.assertEqual(parts_list[0].body, 'I am a perfectionist')
        self.assertEqual(parts_list[1].header, u'adrian')
        self.assertEqual(parts_list[1].body, 'I have a deadline')

    def testPartAnnotation(self):
        '''this is more about testing the annotatext app '''
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        part = self.meeting_1.parts.list()[0]
        res = self.client.post(reverse('annotatetext-post_annotation'),
                        {'selection_start': 7,
                         'selection_end': 14,
                         'flags': 0,
                         'color': '#000',
                         'lengthcheck': len(part.body),
                         'comment' : 'just perfect',
                         'object_id': part.id,
                         'content_type': ContentType.objects.get_for_model(part).id,
                        })
        self.assertEqual(res.status_code, 302)
        annotation = Annotation.objects.get(object_id=part.id,
                         content_type=ContentType.objects.get_for_model(part).id)
        self.assertEqual(annotation.selection, 'perfect')
        # ensure the activity has been recorded
        stream = Action.objects.stream_for_actor(self.jacob)
        self.assertEqual(stream.count(), 3)
        self.assertEqual(stream[0].verb, 'started following')
        self.assertEqual(stream[0].target.id, self.meeting_1.id)
        self.assertEqual(stream[1].verb, 'got badge')
        self.assertEqual(stream[2].verb, 'annotated')
        self.assertEqual(stream[2].target.id, annotation.id)
        # ensure we will see it on the committee page
        annotations = self.committee_1.annotations
        self.assertEqual(annotations.count(), 1)
        self.assertEqual(annotations[0].comment, 'just perfect')


    def testAnnotationForbidden(self):
        self.jacob.groups.clear() # invalidate this user's email
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        part = self.meeting_1.parts.list()[0]
        res = self.client.post(reverse('annotatetext-post_annotation'),
                        {'selection_start': 7,
                         'selection_end': 14,
                         'flags': 0,
                         'color': '#000',
                         'lengthcheck': len(part.body),
                         'comment' : 'just perfect',
                         'object_id': part.id,
                         'content_type': ContentType.objects.get_for_model(part).id,
                        })
        self.assertEqual(res.status_code, 403) # 403 Forbidden. 302 means a user with unverified email has posted an annotation. 

    def testCommitteeList(self):
        res = self.client.get(reverse('committee-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'committees/committee_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.committee_1.id, self.committee_2.id, ])

    def testCommitteeMeetings(self):
        res = self.client.get(self.committee_1.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'committees/committee_detail.html')
        object_list = res.context['meetings_list']
        self.assertEqual(map(just_id, object_list), 
                         [self.meeting_1.id, self.meeting_2.id, ], 
                         'object_list has wrong objects: %s' % object_list)

    def testLoginRequired(self):
        res = self.client.post(reverse('committee-meeting',
                           kwargs={'pk': self.meeting_1.id}))
        self.assertFalse(self.bill_1 in self.meeting_1.bills_first.all())
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res['location'].startswith('%s%s'  %
                                       ('http://testserver', settings.LOGIN_URL)))

    def testConnectToMK(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.post(reverse('committee-meeting',
                           kwargs={'pk': self.meeting_1.id}),
                               {'user_input_type': 'mk',
                                'mk_name': self.mk_1.name})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(self.meeting_1 in self.mk_1.committee_meetings.all())
        self.client.logout()

    def testConnectToBill(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.post(reverse('committee-meeting',
                                       kwargs={'pk':
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
        self.group.delete()
        self.bill_1.delete()
        self.mk_1.delete()
        
class AgendaTopicsTest(TestCase):

    def setUp(self):
        self.committee_1 = Committee.objects.create(name='c1')
        self.committee_2 = Committee.objects.create(name='c2')
        self.meeting_1 = self.committee_1.meetings.create(date=datetime.now(),
                                 protocol_text='''jacob:
I am a perfectionist
adrian:
I have a deadline''')
        self.meeting_1.create_protocol_parts()
        self.meeting_2 = self.committee_1.meetings.create(date=datetime.now(),
                                                         protocol_text='m2')
        self.meeting_2.create_protocol_parts()
        self.jacob = User.objects.create_user('jacob', 'jacob@example.com',
                                              'JKM')
        self.ofri = User.objects.create_user('ofri', 'ofri@example.com',
                                              'ofri')
        (self.group, created) = Group.objects.get_or_create(name='Valid Email')
        if created:
            self.group.save()
        self.group.permissions.add(Permission.objects.get(name='Can add topic'))
        self.jacob.groups.add(self.group)
        self.mk_1 = Member.objects.create(name='mk 1')
        self.topic_1 = Topic.objects.create(creator=self.ofri, title="hello", description="hello world")

    def testBasic(self):
        agenda_topic = AgendaTopic.objects.create(
            editor=self.jacob, topic=self.topic_1, committee=self.committee_1)
        self.assertEqual(self.committee_1.get_public_topics(), [topic])
        agenda_topic.set_status(topic, "rejected", "because I feel like it")
        self.assertEmpty(self.committee_1.get_topics_topics())
