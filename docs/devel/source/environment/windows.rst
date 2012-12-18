===========
MS Windows
===========

On MS Windows the process is more manual. We'll start by downloading and
installing Python and some packages.

Python and packages
====================

Python
--------

`Download the latest Python 2.7`_ MSI installer matching your architecture
(32 or 64 bit). As of this writing, the latest one is `2.7.3`_.

.. _2.7.3: http://www.python.org/download/releases/2.7.3/
.. _Download the latest Python 2.7: http://python.org/download/releases/

Once downloaded, run the installer, and accept defaults (if you know what you're
doing and wish to, adjust them):

.. image:: python27_win.png
 
distribute
---------------

distribute replaces setuptools and makes our windows install simpler (as 
setuptools for python2.7 on windows has problems on 64bit).

`Download distribute`_ for your architecture and install it.

.. image:: distribute_win.png

.. _Download distribute: http://www.lfd.uci.edu/~gohlke/pythonlibs/#distribute

pip and virtualenv
----------------------

We'll install them with distribute. Open a command window, and::

    cd c:\Python27\Scripts
    easy_install pip virtualenv

PIL and lxml
--------------

Since compiling those packages (inside the virtualenv) is not an easy task,
we'll download and use installers for them, and instruct virtualenv to use
Python's global site-packages (not pure, but will make things easier for MS
Windows developers).

Download and install the installers matching your architecture for:

- PIL_
- lxml_ (version 2.3.x)

.. _PIL: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pil
.. _lxml: http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml


git and GitHub
================

The Open Knesset code is hosted on GitHub, and uses ``git`` for distributed
version control. The easiest way to install them on windows is with
`GitHub for Windows`_ (download from the top right corner).

Run the installer, it'll start and download the rest of the needed packages:

.. image:: github_tools_win.png

.. _GitHub for Windows: http://windows.github.com



Proceed to :ref:`github`
