=======
OS X
=======

.. important::

    The info here is based on the post
    `Fixing Python, virtualenv and pip on Mountain Lion`_
    
.. _Fixing Python, virtualenv and pip on Mountain Lion: http://blog.dyve.net/fixing-python-virtualenv-and-pip-on-mountain

Command Line Tools
=====================

* Go to https://developer.apple.com/downloads
* Search for command line tools
* Download and install the version right for your OS

Install pip and virtualenv
========================================

.. code-block:: sh

    sudo easy_install pip
    sudo pip install virtualenv

Install basic dependencies
========================================

Install homebrew:

.. code-block:: sh

    ruby -e "$(curl -fsSkL raw.github.com/mxcl/homebrew/go)"

Install python libraries dependencies:

.. code-block:: sh

    brew install jpeg libpng libxml2 libxslt
    
Add locale settings (in case you're not UTF-8), in your ``~/.bashrc``:


.. code-block:: bash

    export LANG="en_US.UTF-8"
    export LC_COLLATE="en_US.UTF-8"
    export LC_CTYPE="en_US.UTF-8"
    export LC_MESSAGES="en_US.UTF-8"
    export LC_MONETARY="en_US.UTF-8"
    export LC_NUMERIC="en_US.UTF-8"
    export LC_TIME="en_US.UTF-8"
    export LC_ALL=

And source them (to have them updated in the current shell):

.. code-block:: sh

    source ~/.bashrc


