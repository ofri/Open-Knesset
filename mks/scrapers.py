# encoding: utf-8

from okscraper.base import BaseScraper
from okscraper.sources import BaseSource
from okscraper.storages import BaseStorage
from mks.models import Member, Event
from urlparse import urlparse, parse_qs
from django.conf import settings
from urllib import quote
from django.db.models import Max
import urllib2
import json
import dateutil.parser

class MksEventsScraper(BaseScraper):
    """
    runs the MkEventsScraper for each mk with a calendar url
    """    
    
    def __init__(self):
        super(MksEventsScraper, self).__init__(self)
        self.source = BaseSource()
        self.storage = BaseStorage()
        
    def _get_google_cal_page(self, calendar_id, sync_token, page_token=None):
        api_key = settings.GOOGLE_CALENDAR_API_KEY
        if page_token is not None:
            param = '&pageToken=%s'%quote(page_token)
        else:
            param = '&syncToken=%s'%quote(sync_token) if sync_token is not None else ''
        url = 'https://content.googleapis.com/calendar/v3/calendars/%s/events?singleEvents=true%s&key=%s' % (quote(calendar_id), param, quote(api_key))
        response = urllib2.urlopen(url)
        data = json.load(response)
        self._getLogger().debug(data)
        res = {}
        res['nextSyncToken'] = data['nextSyncToken'] if 'nextSyncToken' in data else None
        res['nextPageToken'] = data['nextPageToken'] if 'nextPageToken' in data else None
        res['items'] = data['items'] if 'items' in data else []
        return res
        
    def _process_items(self, mk, items):
        self._getLogger().info('processing %s items' % len(items))
        for item in items:
            start_date = dateutil.parser.parse(item['start']['dateTime']) if 'start' in item and 'dateTime' in item['start'] else None
            end_date = dateutil.parser.parse(item['end']['dateTime']) if 'end' in item and 'dateTime' in item['end'] else None
            if start_date is None or end_date is None:
                self._getLogger().error('invalid start / end date')
            else:
                # assuming timezone is always israel because I can't seem to save timezone to sqlite
                start_date = start_date.replace(tzinfo=None)
                end_date = end_date.replace(tzinfo=None)
                link = item['htmlLink'] if 'htmlLink' in item else None
                summary = item['summary'] if 'summary' in item else None
                description = item['description'] if 'description' in item else None
                data = unicode(item)
                Event(member=mk, start_date=start_date, end_date=end_date, link=link, summary=summary, description=description, data=data).save()
        
    def _scrape(self):
        for mk in Member.objects.filter(calendar_url__isnull=False):
            qs = parse_qs(urlparse(mk.calendar_url).query)
            self._getLogger().info('processing mk %s' % mk.id)
            if 'src' not in qs:
                self._getLogger().warn('invalid calendar url for mk %s: %s' % (mk.id, mk.calendar_url))
            else:
                calendar_id = qs['src'][0]
                self._getLogger().debug('processing calendar_id: %s' % calendar_id)
                res = self._get_google_cal_page(calendar_id, mk.calendar_sync_token)
                self._process_items(mk, res['items'])
                while res['nextPageToken'] is not None:
                    self._getLogger().debug('processing next page..')
                    res = self._get_google_cal_page(calendar_id, None, res['nextPageToken'])
                    self._process_items(mk, res['items'])
                if res['nextSyncToken'] is None:
                    self._getLogger().error('did not get nextToken!')
                else:
                    mk.calendar_sync_token = res['nextSyncToken']
                    mk.save()
                
            

