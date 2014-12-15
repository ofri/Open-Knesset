#encoding: UTF-8
from django.conf.urls import url, patterns
from views import MainScraperStatusView, ScraperRunDetailView


auxiliarysurlpatterns = patterns('',
    url(r'^scrapers/$', MainScraperStatusView.as_view(), name='main-scrapers-status'),
    url(r'^scraper/(?P<pk>\d+)$', ScraperRunDetailView.as_view(), name='scraper-log'),
)
