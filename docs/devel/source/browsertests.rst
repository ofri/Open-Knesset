.. _browser_tests:

=================
Browser testing
=================

Running Browser Tests
=======================

Browser tests are run with a different test runner, so running ./manage.py test will not run the browser tests.

Instead, you have to specify a different test runner:

.. code-block:: sh

    ./manage.py test --testrunner=knesset.browser_test_runner.Runner

This test runner looks for files that start with browser_cases and runs only the tests contained in those files.

You can run the tests locally - on your own browser, or remotely:

Running tests locally
---------------------

By default the tests run locally using Firefox. You can specify a different browser using the --browser parameter.

.. code-block:: sh

    ./manage.py test --testrunner=knesset.browser_test_runner.Runner --browser=Chrome

The tests are run using selenium, check the selenium docs for available browser options: http://selenium-python.readthedocs.org/api.html

Running tests remotely - using SauceLabs
-----------------------------------------

A better option for running tests is using the SauceLabs service (https://saucelabs.com/). You will first need a username and access key - we have an open source license for SauceLabs but to avoid misuse we can't provide it here, ask your fellow Open Knesset developer for this.

To use SauceLabs you first need to setup a tunnel from your local server to their remote service. This is done using Sauce Connect, see the SauceLabs docs for how to install and use it: https://docs.saucelabs.com/reference/sauce-connect/

Once you have the Sauce Connect tunner working using the username and accesskey, you can run the tests:

.. code-block:: sh

    ./manage.py test --testrunner=knesset.browser_test_runner.Runner --browser=Sauce --sauce-user=OpenKnesset --sauce-accesskey=ACCESS_KEY

In the test output you can find links to the test sessions, something like this: https://saucelabs.com/jobs/0383bb8bb3094a35b36edfd4e68aa094

Note that all the test sessions are publicly available because we have an open source license.

Writing tests
=============

Tests are written using the python selenium bindings and the standard django unit tests framework.

All browser test file names must be in the format browser_cases*.py

You can see a simple test in knesset/browser_cases.py - it is commented with useful details.

Refer to the selenium python documentation for help on using selenium: http://selenium-python.readthedocs.org
