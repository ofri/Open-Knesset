from django.db import models


class SuggestionsManager(models.Manager):

    def create_suggestion(self, **kwargs):
        """Creates a suggestion, and notifies editors"""

        suggestion = self.create(**kwargs)

        # TODO email editors

        return suggestion
