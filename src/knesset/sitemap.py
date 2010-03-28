from django.contrib.sitemaps import Sitemap
from knesset.mks.models import Member, Party
from knesset.laws.models import Vote
from knesset.committees.models import Committee,CommitteeMeeting

class MemberSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Member.objects.all()

class PartySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.55

    def items(self):
        return Party.objects.all()
    
class VoteSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Vote.objects.all()

class CommitteeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Committee.objects.all()

class CommitteeMeetingSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return CommitteeMeeting.objects.all()

class IndexPagesSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0
    def items(self): return ['/', '/vote/', '/member/', '/party/', '/committee/', '/about/']
    def location(self, obj): return obj



sitemaps = {
    'members': MemberSitemap,
    'parties': PartySitemap,
    'votes': VoteSitemap,
    'committees': CommitteeSitemap, 
    'committees_meetings': CommitteeMeetingSitemap,
    'index': IndexPagesSitemap,
}

