import datetime
from haystack import indexes
from haystack import site
from knesset.mks.models import Member, Party


class MemberIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Member.objects.all() 


site.register(Member, MemberIndex)

class PartyIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Party.objects.all() 


site.register(Party, PartyIndex)


