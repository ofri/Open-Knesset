from lobbyists_index import LobbyistsIndexScraper
from lobbyist import LobbyistScraper
from lobbyist_represent import LobbyistRepresentScraper

from okscraper.base import BaseScraper
from okscraper.sources import ScraperSource
from okscraper.storages import ListStorage

class LobbyistsScraper(BaseScraper):

    def __init__(self):
        self.source = ScraperSource(LobbyistsIndexScraper())
        self.storage = ListStorage()

    def _scrape(self):
        lobbyist_ids = self.source.fetch()
        for lobbyist_id in lobbyist_ids:
            lobbyistScraper = LobbyistScraper()
            lobbyist = lobbyistScraper.scrape(lobbyist_id)
            representScraper = LobbyistRepresentScraper()
            lobbyist['represent'] = representScraper.scrape(lobbyist_id)
            self.storage.store(lobbyist)
