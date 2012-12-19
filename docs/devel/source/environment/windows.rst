===========
MS Windows
===========

Installing Initial Requirements
=================================

On MS Windows the process is more manual. We'll start by downloading and
installing Python and some packages.

Python and packages
--------------------

Python
~~~~~~~~

`Download the latest Python 2.7`_ MSI installer matching your architecture
(32 or 64 bit). As of this writing, the latest one is `2.7.3`_.

.. _2.7.3: http://www.python.org/download/releases/2.7.3/
.. _Download the latest Python 2.7: http://python.org/download/releases/

Once downloaded, run the installer, and accept defaults (if you know what you're
doing and wish to, adjust them):

.. image:: python27_win.png
 
distribute
~~~~~~~~~~~~~~~

distribute replaces setuptools and makes our windows install simpler (as 
setuptools for python2.7 on windows has problems on 64bit).

`Download distribute`_ for your architecture and install it.

.. image:: distribute_win.png

.. _Download distribute: http://www.lfd.uci.edu/~gohlke/pythonlibs/#distribute

pip and virtualenv
~~~~~~~~~~~~~~~~~~~~~~

We'll install them with distribute. Open a command window, and::

    cd c:\Python27\Scripts
    easy_install pip virtualenv

PIL and lxml
~~~~~~~~~~~~~~

Since compiling those packages (inside the virtualenv) is not an easy task,
we'll download and use installers for them, and instruct virtualenv to use
Python's global site-packages (not pure, but will make things easier for MS
Windows developers).

Download and install the installers matching your architecture for:

- PIL_
- lxml_ (version 2.3.x)

.. _PIL: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pil
.. _lxml: http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml


git and GitHub tools
=======================

The Open Knesset code is hosted on GitHub, and uses ``git`` for distributed
version control. The easiest way to install them on windows is with
`GitHub for Windows`_ (download from the top right corner).

Run the installer, it'll start and download the rest of the needed packages:

.. image:: github_tools_win.png

.. _GitHub for Windows: http://windows.github.com

Run the GitHub program (you should have an icon on the desktop), and sign in
with your username and password. This should also extract git, and create an ssh
keys and upload the public one to GitHub.


Creating and Activating the virtualenv
===========================================

From the desktop (or programs menu) run the `Git Shell`, it's a shell with git
already configured, in the shell::

    cd C:\
    C:\Python27\Scripts\virtualenv --distribute --system-site-packages oknesset

We need to `activate` the virtual environment (it mainly modifies the paths so
that correct packages and bin directories will be found) each time we wish to
work on the code. ::

    cd oknesset
    Scripts\activate

Note the changed prompt with includes the virtualenv's name.


Getting the Source Code (a.k.a Cloning)
=========================================

Now we'll clone the forked repository into the virutalenv.  Make sure you're in
the `oknesset` directory and run::

    git clone git@github.com:your-name/Open-Knesset.git

Replace `your-username` with the username you've registered at git hub.

Installing requirements
=============================

In the Git Shell command window, with the virtualenv activated,
inside the *oknesset* directory, run:

.. code-block:: sh

    pip install -r Open-Knesset/requirements.txt

And wait ... See an example in the following screenshot:

.. image:: git_shell.png
