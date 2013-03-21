from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from mks.models import Member, Party
from committees.models import Committee
from .models import Suggestion


class SuggestionsTests(TestCase):

    MK_SITE = 'http://mk1.example.com'

    def setUp(self):
        self.member1 = Member.objects.create(name='mk_1')
        self.member2 = Member.objects.create(name='mk_2')
        self.regular_user = User.objects.create_user('reg_user')
        self.editor = User.objects.create_superuser(
            'admin', 'admin@example.com', 'passwd')
        self.party = Party.objects.create(name='party')
        self.committee = Committee.objects.create(name='comm')

    def test_simple_text_suggestion(self):

        suggestion = Suggestion.objects.create_suggestion(
            suggested_by=self.regular_user,
            subject=self.member1,
            action=Suggestion.SET,
            field='website',
            content=self.MK_SITE
        )

        self.assertIsNone(self.member1.website)
        suggestion.auto_apply(self.editor)

        mk = Member.objects.get(pk=self.member1.pk)
        self.assertEqual(mk.website, self.MK_SITE)

        suggestion = Suggestion.objects.get(pk=suggestion.pk)

        self.assertEqual(suggestion.resolved_status, Suggestion.FIXED)
        self.assertEqual(suggestion.resolved_by, self.editor)
        self.assertIsNotNone(suggestion.resolved_at)

        # cleanup
        mk.website = None
        mk.save()

        self.member1 = mk
        Suggestion.objects.all().delete()

    def test_relation_set_suggestion(self):

        suggestion = Suggestion.objects.create_suggestion(
            suggested_by=self.regular_user,
            subject=self.member1,
            action=Suggestion.SET,
            field='current_party',
            suggested_object=self.party
        )
        suggestion.auto_apply(self.editor)

        mk = Member.objects.get(pk=self.member1.pk)
        self.assertEqual(mk.current_party, self.party)

        # cleanup
        mk.current_party = None
        mk.save()

        self.member1 = mk
        Suggestion.objects.all().delete()

    def test_m2m_set_suggestion(self):

        suggestion = Suggestion.objects.create_suggestion(
            suggested_by=self.regular_user,
            subject=self.committee,
            action=Suggestion.SET,
            field='members',
            suggested_object=self.member1
        )
        suggestion.auto_apply(self.editor)

        self.assertEqual(list(self.committee.members.all()), [self.member1])

        # cleanup
        self.committee.members.clear()
        Suggestion.objects.all().delete()

    def test_m2m_add_remove_suggestion(self):
        # make sure we're starting clean
        self.assertEqual(self.committee.members.count(), 0)

        suggestion1 = Suggestion.objects.create_suggestion(
            suggested_by=self.regular_user,
            subject=self.committee,
            action=Suggestion.ADD,
            field='members',
            suggested_object=self.member1
        )
        suggestion2 = Suggestion.objects.create_suggestion(
            suggested_by=self.regular_user,
            subject=self.committee,
            action=Suggestion.ADD,
            field='members',
            suggested_object=self.member2
        )
        suggestion3 = Suggestion.objects.create_suggestion(
            suggested_by=self.regular_user,
            subject=self.committee,
            action=Suggestion.REMOVE,
            field='members',
            suggested_object=self.member1
        )

        suggestion1.auto_apply(self.editor)
        self.assertItemsEqual(self.committee.members.all(), [self.member1])

        suggestion2.auto_apply(self.editor)
        self.assertItemsEqual(
            self.committee.members.all(), [self.member1, self.member2])

        suggestion3.auto_apply(self.editor)
        self.assertItemsEqual(self.committee.members.all(), [self.member2])

        # cleanup
        self.committee.members.clear()
        Suggestion.objects.all().delete()

    def test_get_pending_suggestions(self):

        total = Suggestion.objects.get_pending_suggestions().count()
        self.assertEqual(total, 0)

        total_mk1 = Suggestion.objects.get_pending_suggestions_for(
            self.member1).count()
        self.assertEqual(total_mk1, 0)

        total_mk2 = Suggestion.objects.get_pending_suggestions_for(
            self.member2).count()
        self.assertEqual(total_mk2, 0)

        suggestion1 = Suggestion.objects.create_suggestion(
            suggested_by=self.regular_user,
            subject=self.member1,
            action=Suggestion.SET,
            field='website',
            content=self.MK_SITE
        )

        suggestion2 = Suggestion.objects.create_suggestion(
            suggested_by=self.regular_user,
            subject=self.member2,
            action=Suggestion.SET,
            field='website',
            content=self.MK_SITE
        )

        total = Suggestion.objects.get_pending_suggestions().count()
        self.assertEqual(total, 2)

        total_mk1 = Suggestion.objects.get_pending_suggestions_for(
            self.member1).count()
        self.assertEqual(total_mk1, 1)

        total_mk2 = Suggestion.objects.get_pending_suggestions_for(
            self.member2).count()
        self.assertEqual(total_mk2, 1)

        suggestion1.auto_apply(self.editor)

        total = Suggestion.objects.get_pending_suggestions().count()
        self.assertEqual(total, 1)

        total_mk1 = Suggestion.objects.get_pending_suggestions_for(
            self.member1).count()
        self.assertEqual(total_mk1, 0)

        suggestions_mks2 = Suggestion.objects.get_pending_suggestions_for(
            self.member2)
        total_mk2 = suggestions_mks2.count()
        self.assertEqual(total_mk2, 1)
        self.assertEqual(list(suggestions_mks2), [suggestion2])

        # cleanup
        Suggestion.objects.all().delete()

    def test_cant_auto_apply_freetext(self):
        suggestion = Suggestion.objects.create_suggestion(
            suggested_by=self.regular_user,
            subject=self.member1,
            action=Suggestion.FREE_TEXT,
            content="A free text comment"
        )

        with self.assertRaises(ValueError):
            suggestion.auto_apply(self.editor)

        # cleanup
        Suggestion.objects.all().delete()

    def test_invalid_add_without_field(self):

        with self.assertRaises(ValidationError):
            Suggestion.objects.create_suggestion(
                suggested_by=self.regular_user,
                subject=self.committee,
                action=Suggestion.ADD,
                suggested_object=self.member1
            )

    def test_free_text_without_content(self):
        with self.assertRaises(ValidationError):
            Suggestion.objects.create_suggestion(
                suggested_by=self.regular_user,
                action=Suggestion.FREE_TEXT,
            )

    def test_invalid_set_without_suggested_object(self):
        with self.assertRaises(ValidationError):
            Suggestion.objects.create_suggestion(
                suggested_by=self.regular_user,
                subject=self.member1,
                action=Suggestion.SET,
                field='current_party',
            )

    def test_invalid_action_withot_subject(self):
        with self.assertRaises(ValidationError):
            Suggestion.objects.create_suggestion(
                suggested_by=self.regular_user,
                action=Suggestion.SET,
                field='current_party',
            )
