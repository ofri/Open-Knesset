from django.contrib.contenttypes.models import ContentType
from django.db import models

from .utils import store_model_or_instance


class SuggestionsManager(models.Manager):

    def create_suggestion(self, subject=None, fields=None, **kwargs):
        """Creates a suggestion, and notifies editors"""

        content = kwargs.get('content', {})

        if subject:
            content['subject'] = store_model_or_instance(subject)

        if fields:
            # prepare field values for storage (specially model instances)
            content_fields = {}

            for field, value in fields.items():
                if isinstance(value, models.Model):
                    value = store_model_or_instance(value)
                elif not isinstance(value, basestring):
                    # Iterable, assume a list of several model instances for
                    # the field(e.g: for m2m relations)
                    if not isinstance(value, basestring):
                        try:
                            value_iter = iter(value)
                            items = []
                            for x in value_iter:
                                if isinstance(x, models.Model):
                                    items.append(store_model_or_instance(x))
                                else:
                                    items.append(x)
                        except TypeError:
                            pass
                content_fields[field] = value
            # TODO handle many instances for field items (e.g: several model
            # instances)
            content['fields'] = content_fields

        kwargs['content'] = content

        suggestion = self.create(**kwargs)
        suggestion.full_clean()  # Ensure Model.clean() validation is called

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
