import datetime
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.test import TestCase
from models import Event

now = datetime.datetime.now()

class SimpleTest(TestCase):
    def setUp(self):
        self.ev1 = Event.objects.create(when=now, what="ev1")

    def testFutureEvent(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        tomorrow = now+datetime.timedelta(1)
        ev2 = Event.objects.create(when=tomorrow, what="ev2")
        self.assertTrue(ev2.is_future)
        ev2.delete()

