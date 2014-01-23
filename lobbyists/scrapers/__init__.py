from lobbyist import LobbyistScraper
from lobbyist_represent import LobbyistRepresentScraper
from lobbyists import LobbyistsScraper
from lobbyists_index import LobbyistsIndexScraper

okscrapers = (
    LobbyistScraper,
    LobbyistRepresentScraper,
    LobbyistsScraper,
    LobbyistsIndexScraper,
)

default_okscrapers = (
    LobbyistsScraper,
)
