# encoding: utf-8

from bs4 import BeautifulSoup
from okscraper.base import BaseScraper
from okscraper.sources import UrlSource, ScraperSource
from okscraper.storages import ListStorage, DictStorage
from models import LobbyistHistory, Lobbyist, LobbyistData, LobbyistRepresent, LobbyistRepresentData
from persons.models import Person
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


class MainScraperListStorage(ListStorage):

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


class MainScraper(BaseScraper):

    def __init__(self):
        super(MainScraper, self).__init__(self)
        self.source = ScraperSource(LobbyistsIndexScraper())
        self.storage = MainScraperListStorage()

    def _scrape(self):
        lobbyist_ids = self.source.fetch()
        for lobbyist_id in lobbyist_ids:
            lobbyist = LobbyistScraper().scrape(lobbyist_id)
            self.storage.store(lobbyist)
            break


class LobbyistScraperDictStorage(DictStorage):

    _commitInterval = -1

    def _get_data_keys(self):
        return ['first_name', 'family_name', 'profession', 'corporation_name', 'corporation_id', 'faction_member', 'faction_name', 'permit_type']

    def _get_represents_data(self, source_id):
        return LobbyistRepresentScraper().scrape(source_id)

    def _get_latest_lobbyist_data(self, lobbyist):
        return lobbyist.latest_data()

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


class LobbyistRepresentListStorage(ListStorage):

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
        lobbyist_represent, is_created = LobbyistRepresent.objects.get_or_create(source_id=value['id'])
        represent_data = self._get_last_lobbyist_represent_data(value)
        if represent_data is None:
            LobbyistRepresentData.objects.create(
                name=value['name'],
                domain=value['domain'],
                type=value['type'],
                lobbyist_represent = lobbyist_represent,
                scrape_time = datetime.now()
            )
        value = lobbyist_represent
        super(LobbyistRepresentListStorage, self)._addValueToData(data, value)


class LobbyistRepresentScraper(BaseScraper):

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
