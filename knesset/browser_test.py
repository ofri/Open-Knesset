# encoding: utf-8
from knesset.browser_test_case import BrowserTestCase, on_platforms

@on_platforms()
class MyTestCase(BrowserTestCase):

    def testHomepage(self):
        self.driver.get(self.live_server_url+'/')
        self.driver.find_element_by_id('tidbitCarousel')
