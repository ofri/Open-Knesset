from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from .managers import SuggestionsManager


class Suggestion(models.Model):
    """Data improvement suggestions.  Designed to implement suggestions queue
    for content editors.

    A suggestion can be either:

    * Automatically applied once approved (for that data needs to to supplied
      and action be one of: ADD, REMOVE, SET. If the the field to be
      modified is a relation manger, `subject` should be provided as
      well.
    * Manually applied, in that case a content should be provided for
      `content`.

    The model is generic is possible, and designed for building custom
    suggestion forms for each content type.


    Some scenarious:

    * User allowed to enter a genric text comment (those can't be auto applied)
        - action: FREE_TEXT
        - content: Requires the comment (not empty)

    * Suggest a model instance for m2m relation (e.g: add Member to Committee):
        - action: ADD
        - subject: the object to work upon (e.g: Committee instance)
        - field: m2m relation name on subject (e.g: 'members')
        - suggested_object: Instance to add to the relation (Member instance)

    * Suggest instance for ForeignKey (e.g: suggest Member's current_party):
        - action: SET
        - subject: the object to work upon (e.g: Member instance)
        - field: FK field name in subject (e.g: 'current_party')
        - suggested_object: Party instance for the ForeignKey

    * Set Model's text field value (e.g: Member's website):
        - action: SET
        - subject: the object to work upon (e.g: Member instance)
        - field: Field name in subject (e.g: 'website')
        - content: The content for the field
    """

    ADD, REMOVE, SET, REPLACE, FREE_TEXT = range(5)

    SUGGEST_CHOICES = (
        (ADD, _('Add related object to m2m relation or new model instance')),
        (REMOVE, _('Remove related object from m2m relation')),
        (SET, _('Set field value. For m2m _replaces_ (use ADD if needed)')),
        (FREE_TEXT, _("Free text suggestion")),
    )

    NEW, FIXED, WONTFIX = 0, 1, 2

    RESOLVE_CHOICES = (
        (NEW, _('New')),
        (FIXED, _('Fixed')),
        (WONTFIX, _("Won't Fix")),
    )

    suggested_at = models.DateTimeField(
        _('Suggested at'), blank=True, default=datetime.now, db_index=True)
    suggested_by = models.ForeignKey(User, related_name='suggestions')

    # the option subject this suggestion is for
    subject_ct = models.ForeignKey(
        ContentType, related_name='suggestion_subject', blank=True, null=True)
    subject_id = models.PositiveIntegerField(blank=True, null=True)
    subject = generic.GenericForeignKey('subject_ct', 'subject_id')

    action = models.PositiveIntegerField(
        _('Suggestion type'), choices=SUGGEST_CHOICES)

    # suggestion can be either a foreign key adding to some related manager,
    # set some content text, etc
    field = models.CharField(
        max_length=255, blank=True, null=True,
        help_text=_('Field or related manager to change'))
    suggested_type = models.ForeignKey(
        ContentType, related_name='suggested_content', blank=True, null=True)
    suggested_id = models.PositiveIntegerField(blank=True, null=True)
    suggested_object = generic.GenericForeignKey('suggested_type', 'suggested_id')

    content = models.TextField(_('Free text'), blank=True, null=True)

    resolved_at = models.DateTimeField(_('Resolved at'), blank=True, null=True)
    resolved_by = models.ForeignKey(
        User, related_name='resolved_suggestions', blank=True, null=True)
    resolved_status = models.IntegerField(
        _('Resolved status'), db_index=True, default=NEW,
        choices=RESOLVE_CHOICES)

    objects = SuggestionsManager()

    class Meta:
        verbose_name = _('Suggestion')
        verbose_name_plural = _('Suggestions')

    def clean(self):

        action = self.action
        field_name = self.field

        # Free text needs no validation
        if action == self.FREE_TEXT:
            if not self.content:
                raise ValidationError("FREE_TEXT requires content")
            else:
                return

        if not self.field:
            raise ValidationError("This type of action requires field")

        if not self.subject:
            raise ValidationError("This type of action requires subject")

        ct_obj = self.subject
        field, model, direct, m2m = ct_obj._meta.get_field_by_name(field_name)

        if (m2m or isinstance(field, models.ForeignKey)) and (
                not self.suggested_object):
            raise ValidationError(
                "This type of action requires suggested_object instance")

    def auto_apply(self, resolved_by):

        action_map = {
            self.SET: self.auto_apply_set,
            self.ADD: self.auto_apply_add,
            self.REMOVE: self.auto_applly_remove,
        }

        action = action_map.get(self.action, None)

        if action is None:
            raise ValueError("{0} can't be auto applied".format(
                self.get_action_display()
            ))

        action()

        self.resolved_by = resolved_by
        self.resolved_status = self.FIXED
        self.resolved_at = datetime.now()

        self.save()

    def auto_apply_set(self):
        "Auto updates a field"

        ct_obj = self.subject

        field_name = self.field
        field, model, direct, m2m = ct_obj._meta.get_field_by_name(field_name)

        if m2m:
            value = [self.suggested_object]
        elif isinstance(field, models.ForeignKey):
            value = self.suggested_object
        else:
            value = self.content

        setattr(ct_obj, field_name, value)
        ct_obj.save()

    def auto_apply_add(self):
        "Auto add to m2m"

        ct_obj = self.subject

        field_name = self.field
        field, model, direct, m2m = ct_obj._meta.get_field_by_name(field_name)

        if not m2m:
            raise ValueError("{0} can be auto applied only on m2m".format(
                self.get_action_display()
            ))

        getattr(ct_obj, field_name).add(self.suggested_object)

    def auto_applly_remove(self):
        "Auto delete from m2m"

        ct_obj = self.subject

        field_name = self.field
        field, model, direct, m2m = ct_obj._meta.get_field_by_name(field_name)

        if not m2m:
            raise ValueError("{0} can be auto applied only on m2m".format(
                self.get_action_display()
            ))

        getattr(ct_obj, field_name).remove(self.suggested_object)
