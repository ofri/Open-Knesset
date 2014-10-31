# encoding: utf-8
from datetime import time, datetime

from django.contrib.auth.models import User

from selenium.webdriver.common.keys import Keys

from knesset.browser_test_case import BrowserTestCase, on_platforms
from models import Vote, Bill

# All browser test cases must inherit from BrowserTestCase which initializes the selenium framework
# also, they must use the @on_platforms decorator. This decorator can run the test case several times - for different browser and platforms.

@on_platforms()
class VoteViewsBrowserTest(BrowserTestCase):
    """
    Test the Vote views in the browser
    """
    def runTest(self):
        pass

    def login(self):
        self.user_name = u'test-user'
        self.user_passwd = u'123456'

        try:
            self.user = User.objects.get(username=self.user_name)
        except:
            # Create new
            self.user = User.objects.create_user(username=self.user_name,
                                                 password=self.user_passwd)

        self.driver.get(self.live_server_url + '/users/login/')
        user_el = self.driver.find_element_by_id('id_username')
        passwd_el = self.driver.find_element_by_id('id_password')
        user_el.send_keys(self.user.username)
        passwd_el.send_keys(self.user_passwd)
        passwd_el.submit()

    def test_bill_form_fields_exist(self):
        self.vote_1 = Vote.objects.create(time=datetime(2001, 9, 11),
                                          title='vote 1')
        self.bill_1 = Bill.objects.create(stage='1', title='Bill 1')

        self.login()

        # inside the tests you can use self.drive which will have a ready selenium driver to use
        self.driver.get('%s/vote/%s' % (self.live_server_url, self.vote_1.id))

        # most functions throw an exception if they don't find what their looking for, so you don't have to assert
        self.driver.find_element_by_id('id_vote_model')
        self.driver.find_element_by_id('id_vote_type')
        self.driver.find_element_by_id('id_bill_model')
