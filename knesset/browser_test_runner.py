# encoding: utf-8

import os
from django.test.runner import DiscoverRunner
from django_nose import NoseTestSuiteRunner
from optparse import make_option
from django.core import management
from django.contrib.auth.management.commands import changepassword
from unittest.result import TestResult

browser = 'Firefox'
sauce_username = ''
sauce_accesskey = ''

sauce_platforms = [
    {"platform": "Mac OS X 10.9", "browserName": "chrome", "version": "35"},
    {"platform": "Windows 8.1", "browserName": "internet explorer", "version": "11"},
    {"platform": "Linux", "browserName": "firefox", "version": "29"}
]

class Runner(DiscoverRunner):
    """
    The browser test runner modifies the following from the default django runner:
    1. default test files pattern is browser_test*.py
    2. doesn't use the test databases - it uses the actual configured database
    3. adds some options for selecting browser to test with / remotely with SauceLabs
    """

    option_list = (
        make_option('-t', '--top-level-directory',
            action='store', dest='top_level', default=None,
            help='Top level of project for unittest discovery.'),
        make_option('-p', '--pattern', action='store', dest='pattern',
            default="browser_cases*.py",
            help='The test matching pattern. Defaults to browser_cases*.py.'),
        make_option('--full-initialization', action='store_true', dest='fullinitialization',
            default=False,
            help='this should only be used when running ci - it initializes the environment from scratch'),
        make_option('--sauce-user', action='store', dest='sauceuser',
            default='',
            help='SauceLabs username (required if browser=Sauce, see https://docs.saucelabs.com/reference/sauce-connect/#managing-multiple-tunnels)'),
        make_option('--sauce-accesskey', action='store', dest='sauceaccesskey',
            default='',
            help='SauceLabs access key (required if browser=Sauce)'),
        make_option('--browser', action='store', dest='browser',
            default='Firefox',
            help='The browser to use for selenium tests default is "Firefox", can also run remotely on sauce labs - see docs')
        )

    def __init__(self, *args, **kwargs):
        global browser, sauce_username, sauce_accesskey
        if os.environ.has_key('KNESSET_BROWSER'):
            browser = os.environ.get('KNESSET_BROWSER')
        else:
            browser = kwargs['browser']
        if browser == 'Sauce':
            if os.environ.has_key('SAUCE_USERNAME'):
                sauce_username = os.environ.get('SAUCE_USERNAME')
            else:
                sauce_username = kwargs['sauceuser']
            if os.environ.has_key('SAUCE_ACCESS_KEY'):
                sauce_accesskey = os.environ.get('SAUCE_ACCESS_KEY')
            else:
                sauce_accesskey = kwargs['sauceaccesskey']
        if 'fullinitialization' in kwargs and kwargs['fullinitialization'] == True:
            self.full_initialization()
        super(Runner, self).__init__(*args, **kwargs)

    def full_initialization(self):
        self.create_superuser()

    def create_superuser(self):
        print('Creating test superuser (admin/123456)')
        management.call_command('createsuperuser', interactive=False, username='admin', email='OpenKnessetAdmin@mailinator.com')
        command = changepassword.Command()
        command._get_pass = lambda *args: '123456'
        command.execute('admin')

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass

    def run_suite(self, suite, **kwargs):
        if browser == 'Sauce' and sauce_accesskey == '' and sauce_username == '':
            print('Sauce selected but no accesskey and username - test suite will not run')
            return TestResult()
        else:
            return super(Runner, self).run_suite(suite, **kwargs)
