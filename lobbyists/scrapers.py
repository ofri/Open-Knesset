# encoding: utf-8

from bs4 import BeautifulSoup
from okscraper.base import BaseScraper
from okscraper.sources import UrlSource, ScraperSource
from okscraper.storages import DictStorage, ListStorage
import okscraper.djangoStorages as djangoStorages
from models import Lobbyist, LobbyistRepresent
from persons.models import Person

class LobbyistScraper(BaseScraper):

    def __init__(self):
        super(LobbyistScraper, self).__init__()
        self.source = UrlSource('http://online.knesset.gov.il/WsinternetSps/KnessetDataService/LobbyistData.svc/View_lobbyist(<<id>>)')
        self.storage = djangoStorages.ModelDictStorage(Lobbyist, {
            'person': djangoStorages.ModelValueRelated(Person, {
                'name': djangoStorages.ModelValueStringConcat('first_name', 'family_name')
            }),
            'knesset_id': 'id'
        })

    def _storeLobbyistDataFromSoup(self, soup):
        lobbyist_id = soup.find('d:lobbyist_id').text.strip()
        self._getLogger().info('got lobbyist id "%s"', lobbyist_id)
        lobbyist = {
            'id': lobbyist_id,
            'first_name': soup.find('d:first_name').text.strip(),
            'family_name': soup.find('d:family_name').text.strip(),
            'profession': soup.find('d:profession').text.strip(),
            'corporation_name': soup.find('d:corporation_name').text.strip(),
            'corporation_id': soup.find('d:corporation_id').text.strip(),
            'faction_member': soup.find('d:faction_member').text.strip(),
            'faction_name': soup.find('d:faction_name').text.strip(),
            'permit_type': soup.find('d:lobyst_permit_type').text.strip()
        }
        self.storage.storeDict(lobbyist)
        self._getLogger().debug(lobbyist)

    def _scrape(self, lobbyist_id):
        html = self.source.fetch(lobbyist_id)
        soup = BeautifulSoup(html)
        return self._storeLobbyistDataFromSoup(soup)

class LobbyistRepresentScraper(BaseScraper):

    def __init__(self):
        super(LobbyistRepresentScraper, self).__init__(self)
        self.source = UrlSource('http://online.knesset.gov.il/WsinternetSps/KnessetDataService/LobbyistData.svc/View_lobbyist(<<id>>)/lobbist_type')
        self.storage = djangoStorages.ModelListDictStorage(LobbyistRepresent, {
            'knesset_id': 'id',
            'lobbyist_id': djangoStorages.ModelValueNone('lobbyist_id')
        })

    def _storeLobbyistRepresentDataFromSoup(self, soup, lobbyist_id, lobbyist = None):
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
        if lobbyist is not None:
            for lobbyist_represent in self.storage.get():
                lobbyist.represents.add(lobbyist_represent)
            lobbyist.save()

    def _scrape(self, lobbyist_id, lobbyist = None):
        html = self.source.fetch(lobbyist_id)
        soup = BeautifulSoup(html)
        return self._storeLobbyistRepresentDataFromSoup(soup, lobbyist_id, lobbyist)

class LobbyistsScraper(BaseScraper):

    def __init__(self):
        super(LobbyistsScraper, self).__init__(self)
        self.source = ScraperSource(LobbyistsIndexScraper())
        self.storage = ListStorage()

    def _scrape(self):
        lobbyist_ids = self.source.fetch()
        for lobbyist_id in lobbyist_ids:
            lobbyistScraper = LobbyistScraper()
            lobbyist = lobbyistScraper.scrape(lobbyist_id)
            representScraper = LobbyistRepresentScraper()
            lobbyist_represents = representScraper.scrape(lobbyist_id, lobbyist)
            self.storage.store((lobbyist, lobbyist_represents))

class LobbyistsIndexScraper(BaseScraper):

    def __init__(self):
        super(LobbyistsIndexScraper, self).__init__(self)
        self.source = UrlSource('http://www.knesset.gov.il/lobbyist/heb/lobbyist.aspx')
        self.storage = ListStorage()

    def _storeLobbyistIdsFromSoup(self, soup):
        elts = soup.findAll(lobbyist_id=True)
        counter = 0
        for elt in elts:
            lobbyist_id = elt.get('lobbyist_id')
            if lobbyist_id.isdigit():
                self.storage.store(lobbyist_id)
                self._getLogger().debug(lobbyist_id)
                counter = counter + 1
        self._getLogger().info('got %s lobbyists', str(counter))

    def _scrape(self):
        html = self.source.fetch()
        soup = BeautifulSoup(html)
        return self._storeLobbyistIdsFromSoup(soup)


okscrapers = [
    LobbyistScraper,
    LobbyistRepresentScraper,
    LobbyistsScraper,
    LobbyistsIndexScraper
]

default_okscrapers = [
    LobbyistsScraper
]
