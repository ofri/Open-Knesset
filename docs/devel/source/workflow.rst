.. _devel_workflow:

=========================
Development Workflow
=========================

Congratulations, we have everything installed, now it's time to start working on
the project. The following describes various scenarios.

.. important::

    - MS Windows users: replace ``./manage.py`` with ``python manage.py``
    - Run the manage.py commands from the `Open-Knesset` directory, with the
      virtualenv activated.


Before Coding
==========================

We need to make sure we're in sync with changes done by others (upstream).

.. important::

    Please do this every time before you start developing:

Update the code and requirements
--------------------------------------

Enter the `Open-Knesset` directory, and run:

.. code-block:: sh

    git pull git@github.com:hasadna/Open-Knesset.git master

If `requirements.txt` was modified, make sure all of them are installed (no harm
running this command event in case of no changes):

    `pip install -r requirements.txt`

.. note::

    We recommend running the pip command from the parent diretory (the
    virtualenv's root), as it may create an ``src`` directory when pulling
    packages from git repos. in that case::


        `pip install -r Open-Knesset/requirements.txt`


Run migrations and tests
--------------------------------

.. code-block:: sh

    ./manage.py migrate
    ./manage.py test

if there are any failures, contact the other developers in the `oknesset-dev`_
group to see if that's something you should worry about.

.. _oknesset-dev: https://groups.google.com/forum/#!forum/oknesset-dev


While Coding
==============

General
---------

- Write tests for everything that you code.
- Keep performance in mind - test the number of db queries your code performs
  using ``./manage.py runserver`` and accessing a page that runs the code you
  changed. See the output of the dev-server before and after your change.

