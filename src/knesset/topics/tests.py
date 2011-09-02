"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from models import *

class SimpleTest(TestCase):
    def setUp(self):
        self.ofri = User.objects.create_user('ofri', 'ofri@example.com',
                                              'ofri')
        self.topic_1 = Topic.objects.create(creator=self.ofri, title="hello", description="hello world")

    def test_topic_list(self):
        res = self.client.get(reverse('topic-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'topics/topic_list.html')
        self.assertQuerysetEqual(res.context['topics'], 
                                 ["<Topic: hello>"])

    def tearDown(self):
        self.topic_1.delete()
        self.ofri.delete()

