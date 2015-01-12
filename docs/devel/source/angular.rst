.. _angular:

===================================
Developing for the Angular frontend
===================================


Pre-Requisites
==============

Instructions were tested on Ubuntu, but should work similarly on Windows

.. code-block:: sh

    # Install nvm, follow instructions here: https://github.com/creationix/nvm
    # After nvm is installed, run the following:
    $ nvm install stable
    # To automatically use the stable node on login, add the following to the bottom of ~/.bashrc:
    nvm use stable
    # Install grunt and bower globally:
    $ npm install bower -g
    $ npm install grunt-cli -g
    # Install rvm with stable ruby, follow instructions here: https://rvm.io/rvm/install
    # Install compass:
    $ gem install compass


Updating node and bower modules
===============================

This is like Python's requirements.txt - should be run from time to time, if requirements were updated.

.. code-block:: sh

    $ cd Open-Knesset/angular
    angular$ npm install
    angular$ bower install


Setting the frontend server's settings
======================================

The angular local settings contains the url to the django backend server.

Just copy Open-Knesset/angular/app/settings.js.dist to settings.js

Then modify if needed (by default it will run with localhost:8000)


Running the front-end development server
========================================

.. code-block:: sh

    # cd Open-Knesset/angular
    angular$ grunt serve

That's it!

