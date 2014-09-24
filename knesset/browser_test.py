# encoding: utf-8

from knesset.browser_test_case import BrowserTestCase, on_platforms

# All browser test cases must inherit from BrowserTestCase which initializes the selenium framework
# also, they must use the @on_platforms decorator. This decorator can run the test case several times - for different browser and platforms.

@on_platforms()
class MyTestCase(BrowserTestCase):

    def testHomepage(self):
        # inside the tests you can use self.drive which will have a ready selenium driver to use
        self.driver.get(self.live_server_url+'/')
        # most functions throw an exception if they don't find what their looking for, so you don't have to assert
        self.driver.find_element_by_id('tidbitCarousel')
