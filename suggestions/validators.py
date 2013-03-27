from django.core.exceptions import ValidationError
from django.db import models

from .consts import (CREATE, ADD, REMOVE, SET)


def validate_suggestion(actions, **suggestion_kwargs):
    """Make sure suggestion is valid"""

    validate_free_text_has_comment(actions, **suggestion_kwargs)
    validate_actions(actions)


def validate_free_text_has_comment(actions, **kwargs):

    if actions:
        return  # If we have actions, it's no a free text comment

    comment = kwargs.get('comment')

    if not comment:
        raise ValidationError('A free text suggestion (without actions) '
                              'requires comment')


def validate_actions(actions):
    "Make sure suggestion's actions are valid"

    if not actions:  # No actions ? Nothing to do here
        return

    # empty subject for operations are valid if CREATE was done prior to them
    # to allow m2m ADD after creating new objects
    create_found = False

    for action in actions:
        action_type = action.get('action')

        if action_type not in (CREATE, ADD, REMOVE, SET):
            raise ValidationError(
                'Invalid action: "action" keyword is required, should be one '
                'of (CREATE, ADD, REMOVE, SET)')

        subject = action.get('subject')
        if action_type != CREATE:
            # actions excluding CREATE need a subject model instance
            if not subject and not create_found:
                raise ValidationError(
                    'Invalid action: "subject" keyword is required for actions '
                    'of (ADD, REMOVE, SET)')

            if not isinstance(subject, models.Model) and not create_found:
                raise ValidationError(
                    'Invalid action: "subject" should be a model instance ')
        else:
            # for CREATE, subject should be a Model class
            if not issubclass(subject, models.Model):
                raise ValidationError(
                    'Invalid action: For CREATE "subject" should be a Model '
                    'subclass')
            create_found = subject

        fields = action.get('fields')

        if not hasattr(fields, 'items'):
            raise ValidationError('Actions require a "fields" dict')

        # Now validate fields, in case of prev CREATE and empty following
        # subject, the the found create
        meta = (subject or create_found)._meta

        for fname, value in fields.items():
            try:
                field, model, direct, m2m = meta.get_field_by_name(fname)
            except models.FieldDoesNotExist:
                raise ValidationError(
                    'Invalid action field: Field "{0}" does '
                    'not exists for "{1.object_name}"'.format(fname, meta))

            target = None

            rel = getattr(field, 'rel', None)
            if rel:
                target = rel.to
            elif m2m:
                target = field.model

            if target and not isinstance(value, target):
                raise ValidationError(
                    'Invalid action: Value for "{0.name}" should be an '
                    'instance of "{1}"'.format(field, target))
