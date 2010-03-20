from django.contrib.sitemaps import Sitemap
from knesset.mks.models import Member, Party
from knesset.laws.models import Vote

class MemberSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Member.objects.all()

class PartySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Party.objects.all()
    
class VoteSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Vote.objects.all()

class IndexPagesSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0
    def items(self): return ['/', '/vote/', '/member/', '/party/', '/about/']
    def location(self, obj): return obj


