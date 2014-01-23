from bs4 import BeautifulSoup

from okscraper.base import BaseScraper
from okscraper.sources import UrlSource
from okscraper.storages import DictStorage

class LobbyistScraper(BaseScraper):

    def __init__(self):
        self.source = UrlSource('http://online.knesset.gov.il/WsinternetSps/KnessetDataService/LobbyistData.svc/View_lobbyist(<<id>>)')
        self.storage = DictStorage()

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
