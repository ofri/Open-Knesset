===========
Linux
===========

On Linux we'll be creating a clean virtualenv, so in addtion we'll need
developer tools (to compile PIL, lxml etc).

Debian and derivatives like Ubuntu and Mint
============================================

.. code-block:: sh

    sudo apt-get install build-essential git python python-dev python-setuptools python-virtualenv python-pip
    sudo apt-get build-dep python-imaging
    sudo apt-get build-dep python-lxml


Fedora
============================================

.. code-block:: sh

    sudo yum groupinstall "Development Tools" "Development Libraries"
    sudo yum install git python python-devel python-setuptools python-virtualenv python-pip libjpeg-turbo-devel libpng-devel libxml2-devel libxslt-devel


Once done, proceed to :ref:`github`.
