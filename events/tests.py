"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

import datetime
from datetime import timedelta
import json

import vobject

from django.test import TestCase
from django.utils import translation
from django.core.urlresolvers import reverse

from models import Event


class ViewTest(TestCase):
    def setUp(self):
        now = datetime.datetime.now()
        self.ev1 = Event.objects.create(when=now, what="ev1")
        self.ev2 = Event.objects.create(
            when=now + timedelta(days=1, seconds=2 * 3600 + 34 * 60),
            when_over=now + timedelta(days=1, hours=2),
            when_over_guessed=False,
            what="future=%s" % ''.join(str(x % 10) for x in xrange(300)))
        self.ev3 = Event.objects.create(
            when=now + timedelta(days=1), what="ev3")

    def testDetailView(self):
        res = self.client.get(self.ev2.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['in_days'], 1)
        self.assertEqual(res.context['in_hours'], 2)
        self.assertEqual(res.context['in_minutes'], 33)

    def tearDown(self):
        self.ev1.delete()
        self.ev2.delete()
        self.ev3.delete()
