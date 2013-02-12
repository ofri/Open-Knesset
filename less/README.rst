===========
Less files
===========

We're using LESS_ (no direct editing of css). If you'd like to contribute to the
design efforts:

Before first run, you'll need::

    git submodule init
    git submodule update


You'll need to have `Node.js`_ installed. After that make sure you have less
installed::

    npm install -g less

Make your changes to the files in the ``less`` directory, and compile the using
(assuming you're in the ``Open-Knesset`` directory)::

    lessc less/app.less static/css/app.css

.. _Node.js: http://nodejs.org/
.. _LESS: http://lesscss.org/#-server-side-usage
