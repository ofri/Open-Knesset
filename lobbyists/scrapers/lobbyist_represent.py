from bs4 import BeautifulSoup

from okscraper.base import BaseScraper
from okscraper.sources import UrlSource
from okscraper.storages import ListStorage

class LobbyistRepresentScraper(BaseScraper):

    def __init__(self):
        super(LobbyistRepresentScraper, self).__init__()
        self.source = UrlSource('http://online.knesset.gov.il/WsinternetSps/KnessetDataService/LobbyistData.svc/View_lobbyist(<<id>>)/lobbist_type')
        self.storage = ListStorage()

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
