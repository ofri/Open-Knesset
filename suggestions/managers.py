from django.contrib.contenttypes.models import ContentType
from django.db import models


class SuggestionsManager(models.Manager):

    def create_suggestion(self, **kwargs):
        """Creates a suggestion, and notifies editors"""

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
