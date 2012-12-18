===================================
The Virtual Environment
===================================

.. important::

    Make sure the basic requirements are installed

The virtualenv will create a separated environment which required packages will
be installed into (without affecting Python's global `site-packages`).

This environment will be activated every time we'll be working on the code,
running the development server, etc.


Creating the virtualenv
=========================

Navigate in a terminal (or command window) to the directory you want the
environment created in (usually under your home directory). We'll name the
created environment ``oknesset``. 

Once in that directory:

Linux
------------

.. code-block:: sh

    virtualenv oknesset

.. warning::

    In case you have both Python 2 and 3 installed, please make sure the virtualenv
    is created with Python 2. If that's not the case, pass the correct python
    executable to the virtualenv command. e.g:

    .. code-block:: sh

        virtualenv -p python2 oknesset
    

MS Windows
------------

Since on MS Windows compiling is a lot harder, we'll instruct virtualenv to use
`site-packages` and pick up PIL and lxml we've installed with the requirements.
This is less pure, but we'll live with that.

In this example we'll create the virtualenv in t C:\

.. code-block:: sh

    cd c:\
    c:\Python27\Scripts\virtualenv --distribute --system-site-packages oknesset


Activating the virtualenv
=============================

We need to `activate` the virtual environment (it mainly modifies the paths so
that correct packages and bin directories will be found) each time we wish to
work on the code.

Linux
------

In Linux we'll source the activation script (to set env vars):

.. code-block:: sh

    cd oknesset/
    . bin/activate

Note the change prompt with includes the virtualenv's name.

MS Windows
----------

We'll run the activation script:

.. code-block:: sh

    cd oknesset
    Scripts\activate

Note the change prompt with includes the virtualenv's name.


Clonging the forked repo
============================
