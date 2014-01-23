# encoding: utf-8

from okscraper.base import ParsingFromFileTestCase
from tests.lobbyists.lobbyist_represent import LobbyistRepresentScraper

class testLobbyistRepresentScraper(ParsingFromFileTestCase):

    maxDiff = None

    def _getScraperClass(self):
        return LobbyistRepresentScraper

    def _getFilename(self):
        return 'lobbist_type_<<id>>.xml'

    def testParsing(self):
        self.assertScrape(
            args=(220,),
            expectedData=[
                {
                    'domain': u'איכות הסביבה, בריאות הציבור, בטיחות בדרכים',
                    'id': u'6954817',
                    'lobbyist_id': u'220',
                    'name': u'ישראל בשביל אופניים',
                    'type': u'קבוע',
                },{
                    'id': u'6954818',
                    'lobbyist_id': u'220',
                    'name': u'אופנים בשביל ירושלים',
                    'type': u'קבוע',
                    'domain': u'תחבורה, התחדשות עירונית, בטיחות בדרכים',
                }
            ]
        )
