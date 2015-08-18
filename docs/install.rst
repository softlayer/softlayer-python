.. _install:

Installation
============

What's Included
---------------
When you install softlayer-python you you will get the following:

* a python package called 'SoftLayer' (casing is important) available in your python path.
* a command-line client placed in your system path named 'slcli'.

Using Pip
---------

Install via pip:
::

	$ pip install softlayer


Debian/Ubuntu
-------------

For Debian "jessie" (currently testing) and Ubuntu 14.04, official system
packages are available. **These are typically a couple versions behind so it is recommended to install from pypi if problems are encountered.**
::

	$ sudo apt-get install python-softlayer


.. _install_from_source:

From Source
-----------

The project is developed on GitHub, at
`https://github.com/softlayer/softlayer-python <https://github.com/softlayer/softlayer-python>`_.

Install from source via pip (requires `git <http://git-scm.com>`_):
::

	$ pip install git+git://github.com/softlayer/softlayer-python.git

You can clone the public repository::

    $ git clone git@github.com:softlayer/softlayer-python.git

Or, Download the `tarball <https://github.com/softlayer/softlayer-python/tarball/master>`_:
::

    $ curl -OL https://github.com/softlayer/softlayer-python/tarball/master

Or, download the `zipball <https://github.com/softlayer/softlayer-python/zipball/master>`_:
::

    $ curl -OL https://github.com/softlayer/softlayer-python/zipball/master

Once you have a copy of the source you can install it with one of the following commands:
::

    $ python setup.py install

Or:
::

    $ pip install .

For more information about working with the source, or contributing to the
project, please see the :ref:`Contribution Guide <api_dev>`.
