import json

from django.contrib.contenttypes.models import ContentType
from django.db import models

from . import consts
from .validators import validate_suggestion


class SuggestionsManager(models.Manager):

    def create_suggestion(self, actions=None, **kwargs):
        """Creates a suggestion with all related models, and notifies editors

        :param actions: The actions for a suggestion (no action means free
                        text comment). If specifed, actions should be an
                        iterable, with each action a dict of fields matching
                        SuggestedAction and a key of 'fields' dict with
                        'field_name': value

                        TODO : Add some example here
        """
        validate_suggestion(actions, **kwargs)
        suggestion = self.create(**kwargs)

        if actions:
            for action_data in actions:
                fields = action_data.pop('fields', None)

                # We make special, ugly exception for CREATE, to allow passing
                # subject as model class, instead of model instance

                if action_data['action'] == consts.CREATE:
                    if action_data['subject']:
                        subject = action_data.pop('subject')
                        action_data.update({
                            'subject_id': None,
                            'subject_type': ContentType.objects.get_for_model(
                                subject)
                        })

                action = suggestion.actions.create(**action_data)
                action.save()

                for field, value in fields.iteritems():
                    if isinstance(value, models.Model):
                        action.action_fields.create(name=field,
                                                    value_object=value)
                    else:
                        # TODO: using json.dumps to serialize values here
                        #       Maybe some other safer way to implement
                        #       this ?
                        action.action_fields.create(
                            name=field,
                            value=json.dumps(value, ensure_ascii=False))

        # TODO email editors

        return suggestion

    def get_pending_suggestions(self):
        qs = super(SuggestionsManager, self).get_query_set().filter(
            resolved_status=consts.NEW)
        return qs

    def get_pending_suggestions_for(self, subject):
        "Return new suggestions for a specific instance or model"

        qs = self.get_pending_suggestions()
        ct = ContentType.objects.get_for_model(subject)

        # is it a model instance ?
        if isinstance(subject, models.Model):
            return qs.filter(actions__subject_type=ct,
                             actions__subject_id=subject.pk)

        return qs.filter(actions__subject_type=ct)
