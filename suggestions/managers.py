import json

from django.contrib.contenttypes.models import ContentType
from django.db import models


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
        suggestion = self.create(**kwargs)

        if actions:
            for action in actions:
                fields = action.pop('fields', None)
                action = suggestion.actions.create(**action)

                if fields:
                    for field, value in fields.iteritems():
                        if isinstance(value, models.Model):
                            action.action_fields.create(name=field,
                                                        value_object=value)
                        else:
                            # TODO: using json.dumps to serialize values here
                            #       Maybe some other safer way to implement
                            #       this ?
                            action.action_fields.create(name=field,
                                                        value=json.dumps(value))

        # TODO email editors

        return suggestion

    def get_pending_suggestions(self):
        qs = super(SuggestionsManager, self).get_query_set().filter(
            resolved_status=self.model.NEW)
        return qs

    def get_pending_suggestions_for(self, subject):
        "Return new suggestions for a specific instance"

        qs = self.get_pending_suggestions()
        ct = ContentType.objects.get_for_model(subject)
        return qs.filter(subject_ct=ct, subject_id=subject.pk)
