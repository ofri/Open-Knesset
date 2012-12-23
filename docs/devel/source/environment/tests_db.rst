.. _tests_develdb:

=============================================
Initial Testing and Development Database
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
