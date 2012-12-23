from django.core.management.base import NoArgsCommand
from django.http import HttpRequest
from django.contrib.sitemaps.views import sitemap
from knesset.sitemap import sitemaps
from django.conf import settings
import os

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        h = HttpRequest()
        s = sitemap(h, sitemaps=sitemaps)
        f = open(os.path.join(settings.MEDIA_ROOT,
                              'sitemap.xml'),'wt')
        f.write(s.content)
        f.close()
