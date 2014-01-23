# encoding: utf-8

from okscraper.base import ParsingFromFileTestCase
from tests.lobbyists.lobbyist import LobbyistScraper

class testLobbyistScraper(ParsingFromFileTestCase):

    def _getScraperClass(self):
        return LobbyistScraper

    def _getFilename(self):
        return 'View_lobbyist_<<id>>.xml'

    def testParsing(self):
        self.assertScrape(
            args=(220,),
            expectedData={
                'corporation_id': u'',
                'corporation_name': u'',
                'faction_member': u'לא',
                'faction_name': u'',
                'family_name': u'אביזוהר',
                'first_name': u'יותם',
                'id': u'220',
                'permit_type': u'קבוע',
                'profession': u''
            }
        )
