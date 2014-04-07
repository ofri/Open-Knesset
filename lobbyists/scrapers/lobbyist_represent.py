# encoding: utf-8

from bs4 import BeautifulSoup
from okscraper.base import BaseScraper
from okscraper.sources import UrlSource, ScraperSource
from okscraper.storages import ListStorage, DictStorage
from lobbyists.models import LobbyistHistory, Lobbyist, LobbyistData, LobbyistRepresent, LobbyistRepresentData
from persons.models import Person
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


class LobbyistRepresentListStorage(ListStorage):
    """
    This storage gets a list of lobbyist represent dicts
    and converts each dict to a LobbyistRepresent object
    It first checks the source_id - if there is already a LobbyistRepresent object with the same id and name,
        it will use it and not create a new object
    then it checks the represents data against the latest represents data for the LobbyistRepresent object
        if the data match - no new LobbyistRepresentData object will be created
    """

    _commitInterval = 1

    def _get_last_lobbyist_represent_data(self, data):
        try:
            last_lobbyist_represent_data = LobbyistRepresentData.objects.filter(scrape_time__isnull=False).latest('scrape_time')
        except ObjectDoesNotExist:
            last_lobbyist_represent_data = None
        if last_lobbyist_represent_data is not None:
            for key in ['name', 'domain', 'type']:
                if data[key] != getattr(last_lobbyist_represent_data, key):
                    last_lobbyist_represent_data = None
                    break
        return last_lobbyist_represent_data

    def _addValueToData(self, data, value):
        lobbyist_represent, is_created = LobbyistRepresent.objects.get_or_create(source_id=value['id'], name=value['name'])
        represent_data = self._get_last_lobbyist_represent_data(value)
        if represent_data is None:
            LobbyistRepresentData.objects.create(
                source_id=value['id'],
                name=value['name'],
                domain=value['domain'],
                type=value['type'],
                lobbyist_represent = lobbyist_represent,
                scrape_time = datetime.now()
            )
        value = lobbyist_represent
        super(LobbyistRepresentListStorage, self)._addValueToData(data, value)


class LobbyistRepresentScraper(BaseScraper):
    """
    This scraper gets a lobbyist id and returns a list of LobbyistRepresent objects for that lobbyist 
    """

    def __init__(self):
        super(LobbyistRepresentScraper, self).__init__(self)
        self.source = UrlSource('http://online.knesset.gov.il/WsinternetSps/KnessetDataService/LobbyistData.svc/View_lobbyist(<<id>>)/lobbist_type')
        self.storage = LobbyistRepresentListStorage()

    def _storeLobbyistRepresentDataFromSoup(self, soup, lobbyist_id):
        self._getLogger().info('got lobbyist represent (lobbyist id "%s")', lobbyist_id)
        for elt in soup.findAll('content'):
            represent = {}
            represent['id'] = elt.find('d:lobbyist_represent_id').text.strip()
            represent['lobbyist_id'] = elt.find('d:lobbyist_id').text.strip()
            represent['name'] = elt.find('d:lobbyist_represent_name').text.strip()
            represent['domain'] = elt.find('d:lobbyist_represent_domain').text.strip()
            represent['type'] = elt.find('d:lobbyist_represent_type').text.strip()
            self._getLogger().debug(represent)
            self.storage.store(represent)

    def _scrape(self, lobbyist_id):
        html = self.source.fetch(lobbyist_id)
        soup = BeautifulSoup(html)
        return self._storeLobbyistRepresentDataFromSoup(soup, lobbyist_id)

