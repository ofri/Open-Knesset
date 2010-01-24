import datetime
from haystack import indexes
from haystack import site
from knesset.laws.models import Vote


class VoteIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    time = indexes.DateTimeField(model_attr='time')
    summary = indexes.CharField(model_attr='summary')
    title = indexes.CharField(model_attr='title')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Vote.objects.filter(summary__isnull=False,
            title__isnull=False, time__isnull=False)


site.register(Vote, VoteIndex)


