.. _tests_develdb:

=============================================
Initial Testing, Development DB & Server
=============================================

After you've installed the base environment, it's time to run the tests and get
an initial development db.

.. important::

    - MS Windows users: repleace ``./manage.py`` with ``python manage.py``
    - Run the manage.py commands from the `Open-Knesset` directory, with the
      virtualenv activated.


Running Tests
==============

.. code-block:: sh

    cd Open-Knesset
    ./manage.py test

Download the Development DB
===============================

Download and extract dev.db from (TBD). Place it in the `Open-Knesset` directory.

To make sure everything is up to date, run the database schema migrations:

.. code-block:: sh

    ./manage.py migrate


You might want to create your own superuser:


.. code-block:: sh

    ./manage.py createsuperuser


Running the Development server
=====================================

To run the development server:

.. code-block:: sh

    ./manage.py runserver

Once done, you can access it via http://localhost:8000 .


Enable django-debug-toolbar
==============================

.. todo:: Expand on this

Create `local_settings.py` in the `knesset` directory (where `settings.py` is
located). To enable the `django-debug-toolbar`_ on the local developement address,
put in that file:

.. _django-debug-toolbar: http://pypi.python.org/pypi/django-debug-toolbar

.. code-block:: python

    INTERNAL_IPS = ('127.0.0.1',)
