API Calls
==============

All examples are show with `curl` from the command line. One can access the URL
and parse the results with their favorite language.

If no format is specified the response will be JSON. For other formats (xml for
now) add the format to the GET params.

e.g:

.. code-block:: sh

    curl http://oknesset.org/api/member/782/?format=xml

.. toctree::
    :maxdepth: 2

    member
    committee
