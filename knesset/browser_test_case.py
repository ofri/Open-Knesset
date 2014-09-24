# encoding: utf-8

import os, sys, new
from selenium import webdriver
from django.test import LiveServerTestCase
from sauceclient import SauceClient
from knesset.browser_test_runner import browser, sauce_accesskey, sauce_username, sauce_platforms


def on_platforms():
    """
    class decorator for the browser test case
    it runs the test case several times for each desired browser/platform
    this decorator must be used on the extending class - not directly on BrowserTestCase
    """
    if browser == 'Sauce':
        platforms = sauce_platforms
    else:
        platforms = [browser]
    def decorator(base_class):
        module = sys.modules[base_class.__module__].__dict__
        for i, platform in enumerate(platforms):
            d = dict(base_class.__dict__)
            d['desired_capabilities'] = platform
            name = "%s_%s" % (base_class.__name__, i + 1)
            module[name] = new.classobj(name, (base_class,), d)
    return decorator


class BrowserTestCase(LiveServerTestCase):
    """
    Base class that initializes the selenium driver for the desired browser/s
    """

    def setUp(self):
        if browser == 'Sauce':
            self.desired_capabilities['name'] = self.id()
            if os.environ.has_key('TRAVIS_JOB_NUMBER'):
                self.desired_capabilities['tunnel-identifier'] = os.environ['TRAVIS_JOB_NUMBER']
                self.desired_capabilities['build'] = os.environ['TRAVIS_BUILD_NUMBER']
                self.desired_capabilities['tags'] = [os.environ['TRAVIS_PYTHON_VERSION'], 'CI']
            sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub"
            self.sauce = SauceClient(sauce_username, sauce_accesskey)
            self.driver = webdriver.Remote(
                desired_capabilities=self.desired_capabilities,
                command_executor=sauce_url % (sauce_username, sauce_accesskey)
            )
            self.driver.implicitly_wait(5)
        else:
            self.driver = getattr(webdriver, browser)()
            self.driver.implicitly_wait(3)

    def tearDown(self):
        if browser == 'Sauce':
            print("\nLink to your job: \n https://saucelabs.com/jobs/%s \n" % self.driver.session_id)
            try:
                if sys.exc_info() == (None, None, None):
                    self.sauce.jobs.update_job(self.driver.session_id, passed=True)
                else:
                    self.sauce.jobs.update_job(self.driver.session_id, passed=False)
            finally:
                self.driver.quit()
        else:
            self.driver.quit()
