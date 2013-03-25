from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import SuggestionsManager
from .utils import load_model_or_instance


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

    ADD, REMOVE, SET, CREATE, FREE_TEXT = range(5)

    SUGGEST_CHOICES = (
        (ADD, _('Add related object to m2m relation or new model instance')),
        (REMOVE, _('Remove related object from m2m relation')),
        (SET, _('Set field value. For m2m _replaces_ (use ADD if needed)')),
        (CREATE, _('Create new model instance')),
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

    action = models.PositiveIntegerField(
        _('Suggestion type'), choices=SUGGEST_CHOICES)

    comment = models.TextField(blank=True, null=True)

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

    @property
    def subject(self):
        """
        Return the subject instance or Model. Allows exceptions to bubble up
        (important for validation in clean() method).

        :rtype: a model instance or Model if found
        :raises: DoesNotExist for invalid pk

        """
        model_or_instance = self.content.get('subject')

        if not model_or_instance:
            return

        return load_model_or_instance(*model_or_instance)

    def clean(self):

        action = self.action
        fields = self.content.get('fields', {})

        subject = self.subject

        # Free text needs no validation
        if action == self.FREE_TEXT:
            if not self.content.get('text'):
                raise ValidationError("FREE_TEXT requires content")
            else:
                return

        if action == self.CREATE:
            pass  # TODO implement create validation

        if not fields:
            raise ValidationError("This type of action requires fields")

        if not subject:
            raise ValidationError("This type of action requires subject")

        for name, value in fields.items():
            try:
                field, model, direct, m2m = subject._meta.get_field_by_name(name)
            except models.FieldDoesNotExist:
                raise ValidationError('Field "{0}" does not exist'.format(name))

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
        "Auto set fields values"

        subject = self.subject
        fields = self.content.get('fields', {})

        for name, value in fields.items():
            field, model, direct, m2m = subject._meta.get_field_by_name(name)

            if m2m:
                value = [load_model_or_instance(*x) for x in value]
            elif isinstance(field, models.ForeignKey):
                value = load_model_or_instance(*value)

            setattr(subject, name, value)
        subject.save()

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


