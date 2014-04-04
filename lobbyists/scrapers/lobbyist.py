# encoding: utf-8

from bs4 import BeautifulSoup
from okscraper.base import BaseScraper
from okscraper.sources import UrlSource, ScraperSource
from okscraper.storages import ListStorage, DictStorage
from lobbyists.models import LobbyistHistory, Lobbyist, LobbyistData, LobbyistRepresent, LobbyistRepresentData
from persons.models import Person
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

from lobbyist_represent import LobbyistRepresentScraper


class LobbyistScraperDictStorage(DictStorage):
    """
    This storage first determines if a new Lobbyist object needs to be created:
        it searches for a Lobbyist object with the same source_id and first / last name
        if such an object exists - it uses that object, otherwise created a new Lobbyist
    It then updates the lobbyist.data:
        it gets the last LobbyistData object for this lobbyist and compares that to the current data
        if it matches - then that object is used and a new object is not created
        else - a new LobbyistData object is created and appended to the lobbyist.data
    This storage returns the lobbyist object
    """

    _commitInterval = -1

    def _get_data_keys(self):
        return ['first_name', 'family_name', 'profession', 'corporation_name', 'corporation_id', 'faction_member', 'faction_name', 'permit_type']

    def _get_represents_data(self, source_id):
        return LobbyistRepresentScraper().scrape(source_id)

    def _get_latest_lobbyist_data(self, lobbyist):
        return lobbyist.latest_data

    def _get_last_lobbyist_data(self, lobbyist, data):
        try:
            last_lobbyist_data = self._get_latest_lobbyist_data(lobbyist)
        except ObjectDoesNotExist:
            last_lobbyist_data = None
        if last_lobbyist_data is not None:
            for key in self._get_data_keys():
                if data[key] != getattr(last_lobbyist_data, key):
                    last_lobbyist_data = None
                    break
        if last_lobbyist_data is not None:
            represent_ids = sorted(data['represents'], key=lambda represent: represent.id)
            last_represent_ids = sorted(last_lobbyist_data.represents.all(), key=lambda represent: represent.id)
            if represent_ids != last_represent_ids:
                last_lobbyist_data = None
        return last_lobbyist_data

    def commit(self):
        super(LobbyistScraperDictStorage, self).commit()
        data = self._data
        source_id = data['id']
        data['represents'] = self._get_represents_data(source_id)
        full_name = '%s %s' % (data['first_name'], data['family_name'])
        q = Lobbyist.objects.filter(source_id=source_id, person__name=full_name)
        if q.count() > 0:
            lobbyist = q[0]
        else:
            lobbyist = Lobbyist.objects.create(person=Person.objects.create(name=full_name), source_id=source_id)
        self._data = lobbyist
        last_lobbyist_data = self._get_last_lobbyist_data(lobbyist, data)
        if last_lobbyist_data is None:
            kwargs = {}
            for key in self._get_data_keys():
                kwargs[key] = data[key]
            kwargs['source_id'] = source_id
            lobbyist_data = LobbyistData.objects.create(**kwargs)
            for represent in data['represents']:
                lobbyist_data.represents.add(represent)
            lobbyist_data.scrape_time = datetime.now()
            lobbyist_data.save()
            lobbyist.data.add(lobbyist_data)
        else:
            lobbyist.data.add(last_lobbyist_data)
        lobbyist.save()

        
class LobbyistScraper(BaseScraper):
    """
    This scraper gets a lobbyist id, it then goes to the knesset api to get the data about the lobbyist
    """

    def __init__(self):
        super(LobbyistScraper, self).__init__()
        self.source = UrlSource('http://online.knesset.gov.il/WsinternetSps/KnessetDataService/LobbyistData.svc/View_lobbyist(<<id>>)')
        self.storage = LobbyistScraperDictStorage()

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
            'permit_type': soup.find('d:lobyst_permit_type').text.strip(),
        }
        self.storage.storeDict(lobbyist)
        self._getLogger().debug(lobbyist)

    def _scrape(self, lobbyist_id):
        html = self.source.fetch(lobbyist_id)
        soup = BeautifulSoup(html)
        return self._storeLobbyistDataFromSoup(soup)
