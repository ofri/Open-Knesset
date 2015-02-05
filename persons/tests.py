from datetime import datetime, date

from django.test import TestCase
from unittest import skip

from .models import Person
from mks.models import Member, Knesset


class PersonTests(TestCase):
    def setUp(self):
        self.knesset = Knesset.objects.create(
            number=1,
            start_date=date(2014,1,1))
        self.defaults = {
            'name': 'The MK',
            'date_of_birth': date.today(),
            'family_status': 'XYZ',
            'place_of_residence': 'AAA',
            'phone': '000-1234',
            'fax': '999-8765',
            'gender': 'F',
        }

    def test_member_person_sync(self):
        """ Test member/person sync on member save() """
        mk = Member.objects.create(**self.defaults)

        self.assertGreater(mk.person.count(), 0)

        person = Person.objects.filter(mk=mk)[0]

        for field in self.defaults:
            self.assertEqual(getattr(mk, field), getattr(person, field))

        mk.delete()
