# encoding: utf-8

from okscraper.base import BaseScraper
from lobbyists.models import Lobbyist, LobbyistCorporation
from committees.models import CommitteeMeeting


class LobbyistCommitteeMeetingsScraper(BaseScraper):
    """
    find committee meetings where a lobbyist is mentioned
    updated the lobbyist.committee_meetings field accordingly
    """

    def scrape(self, lobbyist_id):
        self._getLogger().info('processing lobbyist %s'%lobbyist_id)
        lobbyist = Lobbyist.objects.get(id=lobbyist_id)
        name = lobbyist.person.name
        if len(name) > 5:
            for meeting in CommitteeMeeting.objects.filter(protocol_text__contains=name):
                if lobbyist.committee_meetings.filter(id=meeting.id).count() == 0:
                    self._getLogger().info('mentioned in meeting id %i'%meeting.id)
                    lobbyist.committee_meetings.add(meeting)


class LobbyistsCommiteeMeetingsScraper(BaseScraper):
    """
    update all the lobbyists with relevant committee meetings they are mentioned in
    """

    def scrape(self):
        lobbyists = Lobbyist.objects.all()
        self._getLogger().info('processing %i lobbyists'%lobbyists.count())
        for lobbyist in lobbyists:
            LobbyistCommitteeMeetingsScraper().scrape(lobbyist.id)


class LobbyistCorporationCommitteeMeetingScraper(BaseScraper):
    """
    find committee meetings where a lobbyist corporation is mentioned
    updated the lobbyist_corporation.committee_meetings field accordingly
    """

    def scrape(self, corporation_id):
        self._getLogger().info('processing corporation %i'%corporation_id)
        corporation = LobbyistCorporation.objects.get(id=corporation_id)
        names = []
        names.append(corporation.name)
        for alias_corp in corporation.alias_corporations:
            names.append(alias_corp.name)
        for name in names:
            if len(name) > 5:
                for meeting in CommitteeMeeting.objects.filter(protocol_text__contains=name):
                    if corporation.committee_meetings.filter(id=meeting.id).count() == 0:
                        self._getLogger().info('mentioned in meeting id %i'%meeting.id)
                        corporation.committee_meetings.add(meeting)


class LobbyistCorporationsCommitteeMeetingsScraper(BaseScraper):
    """
    Scraper that links committee meetings with lobbyist corporations
    """

    def scrape(self):
        corporations = LobbyistCorporation.objects.all()
        self._getLogger().info('processing %i lobbyist corporations'%corporations.count())
        for corporation in corporations:
            LobbyistCorporationCommitteeMeetingScraper().scrape(corporation.id)
