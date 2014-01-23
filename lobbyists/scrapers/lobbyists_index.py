from bs4 import BeautifulSoup

from okscraper.base import BaseScraper
from okscraper.sources import UrlSource
from okscraper.storages import ListStorage

class LobbyistsIndexScraper(BaseScraper):

    def __init__(self, *args, **kwargs):
        super(LobbyistsIndexScraper, self).__init__(*args, **kwargs)
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
