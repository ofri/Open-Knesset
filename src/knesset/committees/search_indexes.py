import datetime
from haystack import indexes
from haystack import site
from models import *


class CommitteeIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Committee.objects.all() 

#site.register(Committee, CommitteeIndex)


class CommitteeMeetingIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return CommitteeMeeting.objects.all() 

#site.register(CommitteeMeeting, CommitteeMeetingIndex)


