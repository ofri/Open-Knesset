from django.contrib.contenttypes.models import ContentType
from django.db import models


class SuggestionsManager(models.Manager):

    def create_suggestion(self, **kwargs):
        """Creates a suggestion, and notifies editors"""

        suggestion = self.create(**kwargs)

        # TODO email editors

        return suggestion

    def get_pending_suggestions(self):
        qs = super(SuggestionsManager, self).get_query_set().filter(
            resolved_status=self.model.NEW)
        return qs

    def get_pending_suggestions_for(self, suggested_object):
        "Return new suggestions for a specific instance"

        qs = self.get_pending_suggestions()
        ct = ContentType.objects.get_for_model(suggested_object)
        return qs.filter(content_type=ct, content_id=suggested_object.pk)
