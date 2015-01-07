# encoding: utf-8

from okscraper.base import BaseScraper
from okscraper.sources import ScraperSource
from okscraper.storages import ListStorage
from lobbyists.models import LobbyistHistory, LobbyistCorporation, LobbyistCorporationData, Lobbyist
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from lobbyist import LobbyistScraper
from lobbyists_index import LobbyistsIndexScraper
from lobbyists_committeemeetings import *

class MainScraperListStorage(ListStorage):
    """
    This storage gets a list of lobbyist objects
    it then checks if the same composition of lobbyists (based on id) is the same as in the last LobbyistHistory object
    if it is - then no new object is created - the last LobbyistHistory object is returned
    else - a new LobbyistHistory object is created with scrape_time as the current time
    after all lobbyists were processed - relevant LobbyistCorporation objects are created
    """

    _commitInterval = -1

    def _get_matching_last_lobbyist_history(self, lobbyist_ids):
        try:
            last_lobbyist_history = LobbyistHistory.objects.filter(scrape_time__isnull=False).latest('scrape_time')
        except ObjectDoesNotExist:
            last_lobbyist_history = None
        if last_lobbyist_history is not None:
            last_lobbyist_ids = sorted(last_lobbyist_history.lobbyists.all(), key=lambda lobbyist: lobbyist.id)
            if (lobbyist_ids != last_lobbyist_ids):
                last_lobbyist_history = None
        return last_lobbyist_history

    def _update_lobbyist_corporations(self, lobbyist_history):
        corporation_lobbyists = {}
        for lobbyist in lobbyist_history.lobbyists.all():
            corporation, is_created = LobbyistCorporation.objects.get_or_create(
                source_id=lobbyist.latest_data.corporation_id, name=lobbyist.latest_data.corporation_name
            )
            if not corporation.id in corporation_lobbyists:
                corporation_lobbyists[corporation.id] = []
            corporation_lobbyists[corporation.id].append(lobbyist.id)
        for corporation_id in corporation_lobbyists:
            lobbyist_ids = sorted(corporation_lobbyists[corporation_id])
            corporation = LobbyistCorporation.objects.get(id=corporation_id)
            need_corporation_data = True
            try:
                corporation_data = corporation.latest_data
                if corporation_data.name == corporation.name and corporation_data.source_id == corporation.source_id:
                    last_lobbyist_ids = map(lambda lobbyist: lobbyist.id, sorted(corporation_data.lobbyists.all(), key=lambda lobbyist: lobbyist.id))
                    if last_lobbyist_ids == lobbyist_ids:
                        need_corporation_data = False
            except ObjectDoesNotExist:
                pass
            if need_corporation_data:
                corporation_data = LobbyistCorporationData.objects.create(
                    name=corporation.name, source_id=corporation.source_id
                )
                for id in lobbyist_ids:
                    corporation_data.lobbyists.add(Lobbyist.objects.get(id=id))
                corporation_data.scrape_time = datetime.now()
                corporation_data.save()
                corporation.data.add(corporation_data)
                corporation.save()

        
        
    def commit(self):
        super(MainScraperListStorage, self).commit()
        lobbyists = self._data
        lobbyist_ids = sorted(lobbyists, key=lambda lobbyist: lobbyist.id)
        last_lobbyist_history = self._get_matching_last_lobbyist_history(lobbyist_ids)
        if last_lobbyist_history is None:
            lobbyist_history = LobbyistHistory()
            lobbyist_history.save()
            lobbyist_history.lobbyists = lobbyists
            lobbyist_history.scrape_time = datetime.now()
            lobbyist_history.save()
            self._data = lobbyist_history
        else:
            self._data = last_lobbyist_history
        self._update_lobbyist_corporations(self._data)


class MainScraper(BaseScraper):
    """
    The main scraper - this scraper does all the work and uses the other scrapers
    """

    def __init__(self):
        super(MainScraper, self).__init__(self)
        self.source = ScraperSource(LobbyistsIndexScraper())
        self.storage = MainScraperListStorage()

    def _scrape(self):
        lobbyist_ids = self.source.fetch()
        i=0
        for lobbyist_id in lobbyist_ids:
            lobbyist = LobbyistScraper().scrape(lobbyist_id)
            self.storage.store(lobbyist)
            i+=1
            #if i>0: break
        self._getLogger().info('looking for mentions of lobbyists in committee meetings')
        LobbyistsCommiteeMeetingsScraper().scrape()
        LobbyistCorporationsCommitteeMeetingsScraper().scrape()


