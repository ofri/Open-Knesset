from django.test import TestCase
from django.contrib.auth.models import User

from mks.models import Member
from .models import Suggestion


class SuggestionsTests(TestCase):

    def setUp(self):
        self.member = Member.objects.create(name='mk_1')
        self.regular_user = User.objects.create_user('reg_user')

    def test_simple_text_suggestion(self):

        MK_SITE = 'http://mk1.example.com'

        suggestion = Suggestion.objects.create_suggestion(
            suggested_by=self.regular_user,
            content_object=self.member,
            suggestion_action=Suggestion.UPDATE,
            suggested_field='website',
            suggested_text=MK_SITE
        )

        self.assertIsNone(self.member.website)
        suggestion.auto_apply()

        mk = Member.objects.get(pk=self.member.pk)
        self.assertEqual(mk.website, MK_SITE)
