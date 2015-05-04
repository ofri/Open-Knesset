# encoding: utf-8

from okscraper.base import BaseScraper
from okscraper.sources import ScraperSource
from okscraper.storages import ListStorage
from lobbyists.models import LobbyistHistory, LobbyistCorporation, LobbyistCorporationData, Lobbyist, LobbyistsChange, LobbyistData
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from lobbyist import LobbyistScraper
from lobbyists_index import LobbyistsIndexScraper
from lobbyists_committeemeetings import *
import json

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

    def _update_lobbyists_changes(self):
        chgs = []

        self._getLogger().info('processing lobbyist changes - deleting all existing changes and re-creating from scratch')
        LobbyistsChange.objects.all().delete()

        self._getLogger().info('lobbyist history (added / deleted lobbyists)')
        prev_lh = None
        for lh in LobbyistHistory.objects.order_by('scrape_time'):
            # look for added / deleted lobbyyists
            if prev_lh == None:
                self._getLogger().debug(lh.scrape_time)
                self._getLogger().debug('first history - all lobbyists considered as added')
                added_lobbyist_ids = [l.pk for l in lh.lobbyists.all()]
                deleted_lobbyist_ids = []
            else:
                prev_lobbyist_ids = set([l.pk for l in prev_lh.lobbyists.all()])
                cur_lobbyist_ids = set([l.pk for l in lh.lobbyists.all()])
                deleted_lobbyist_ids = list(prev_lobbyist_ids.difference(cur_lobbyist_ids))
                added_lobbyist_ids = list(cur_lobbyist_ids.difference(prev_lobbyist_ids))
                if len(deleted_lobbyist_ids) > 0 or len(added_lobbyist_ids) > 0:
                    self._getLogger().debug(lh.scrape_time)
                    self._getLogger().debug('%s deleted lobbyists, %s added lobbyists'%(len(deleted_lobbyist_ids), len(added_lobbyist_ids)))

            for lid in added_lobbyist_ids: chgs.append(LobbyistsChange(date=lh.scrape_time, content_object=Lobbyist.objects.get(pk=lid), type='added'))
            for lid in deleted_lobbyist_ids: chgs.append(LobbyistsChange(date=lh.scrape_time, content_object=Lobbyist.objects.get(pk=lid), type='deleted'))
            prev_lh = lh

        self._getLogger().info('lobbyist data (lobbyist metadata changes)')
        lds = {}
        for ld in LobbyistData.objects.order_by('scrape_time'):
            lid = ld.lobbyist.pk
            if lid in lds:
                # we don't add an event for new lobbyist data, assuming you will get a lobbyist added event from the lobbyist history
                changeset = []
                prev_ld = lds[lid]
                # looking for changes in the lobbyist data fields
                for field in ['source_id', 'first_name', 'family_name', 'profession', 'corporation_name', 'corporation_id', 'faction_member', 'faction_name', 'permit_type']:
                    if getattr(prev_ld, field) != getattr(ld, field):
                        changeset.append((field, getattr(prev_ld, field), getattr(ld, field)))
                # looking for changes in the lobbyist represents
                # we use only the name because there are some problems with the other represents fields
                prev_represents = set([r.name for r in prev_ld.represents.all()])
                cur_represents = set([r.name for r in ld.represents.all()])
                deleted_represent_names = list(prev_represents.difference(cur_represents))
                if len(deleted_represent_names) > 0: changeset.append(('represent_names', 'deleted', deleted_represent_names))
                added_represent_names = list(cur_represents.difference(prev_represents))
                if len(added_represent_names) > 0: changeset.append(('represent_names', 'added', added_represent_names))
                if len(changeset) > 0:
                    self._getLogger().debug('%s: got %s changes'%(ld.scrape_time, len(changeset)))
                    chgs.append(LobbyistsChange(date=ld.scrape_time, content_object=ld.lobbyist, type='modified', extra_data=json.dumps(changeset)))
            lds[lid] = ld

        self._getLogger().info('lobbyist corporation data')
        lcds = {}
        for lcd in LobbyistCorporationData.objects.order_by('scrape_time'):
            lc = lcd.corporation
            lcid = lc.pk
            if lcid in lcds:
                # existing corporation - need to check for changes
                changeset = []
                prev_lcd = lcds[lcid]
                for field in ['name', 'source_id']:
                    if getattr(prev_lcd, field) != getattr(lcd, field):
                        changeset.append((field, getattr(prev_lcd, field), getattr(lcd, field)))
                prev_lobbyists = set([l.pk for l in prev_lcd.lobbyists.all()])
                cur_lobbyists = set([l.pk for l in lcd.lobbyists.all()])
                deleted_lobbyists = list(prev_lobbyists.difference(cur_lobbyists))
                if len(deleted_lobbyists) > 0: changeset.append(('lobbyists', 'deleted', deleted_lobbyists))
                added_lobbyists = list(cur_lobbyists.difference(prev_lobbyists))
                if len(added_lobbyists) > 0: changeset.append(('lobbyists', 'added', added_lobbyists))
                if len(changeset) > 0:
                    self._getLogger().debug('%s: got %s changes'%(lcd.scrape_time, len(changeset)))
                    chgs.append(LobbyistsChange(date=lcd.scrape_time, content_object=lc, type='modified', extra_data=json.dumps(changeset)))
            else:
                # new coropration
                chgs.append(LobbyistsChange(date=lcd.scrape_time, content_object=lc, type='added'))
            lcds[lcid] = lcd

        self._getLogger().info('bulk creating %s changes'%len(chgs))
        LobbyistsChange.objects.bulk_create(chgs)

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
        self._update_lobbyists_changes()
