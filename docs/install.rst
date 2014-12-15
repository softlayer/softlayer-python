.. _install:

Installation
============

Using Pip
---------

Install via pip: ::

	$ pip install softlayer


Debian/Ubuntu
-------------

For Debian "jessie" (currently testing) and Ubuntu 14.04, official system
packages are available::

	$ sudo apt-get install python-softlayer


.. _install_from_source:

From Source
-----------

The project is developed on GitHub, at
`https://github.com/softlayer/softlayer-python <https://github.com/softlayer/softlayer-python>`_.

Install from source via pip (requires `git <http://git-scm.com>`_): ::

	$ pip install git+git://github.com/softlayer/softlayer-python.git

You can clone the public repository::

    $ git clone git@github.com:softlayer/softlayer-python.git

Or, Download the `tarball <https://github.com/softlayer/softlayer-python/tarball/master>`_::

    $ curl -OL https://github.com/softlayer/softlayer-python/tarball/master

Or, download the `zipball <https://github.com/softlayer/softlayer-python/zipball/master>`_::

    $ curl -OL https://github.com/softlayer/softlayer-python/zipball/master

Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages easily::

    $ python setup.py install

For more information about working with the source, or contributing to the
project, please see the :ref:`Contribution Guide <api_dev>`.
