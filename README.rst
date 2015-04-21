SoftLayer API Python Client
===========================
.. image:: https://travis-ci.org/softlayer/softlayer-python.svg?branch=master
    :target: https://travis-ci.org/softlayer/softlayer-python

.. image:: https://landscape.io/github/softlayer/softlayer-python/master/landscape.png
    :target: https://landscape.io/github/softlayer/softlayer-python/master

.. image:: https://badge.fury.io/py/SoftLayer.png
    :target: http://badge.fury.io/py/SoftLayer

.. image:: https://coveralls.io/repos/softlayer/softlayer-python/badge.svg
    :target: https://coveralls.io/r/softlayer/softlayer-python

SoftLayer API bindings for Python. For use with
`SoftLayer's API <http://sldn.softlayer.com/reference/softlayerapi>`_.

This library provides a simple interface to interact with SoftLayer's XML-RPC
API and provides support for many of SoftLayer API's features like
`object masks <http://sldn.softlayer.com/article/Using-Object-Masks-SoftLayerAPI>`_
and includes a command-line interface that can be used to manage various
SoftLayer services.


Documentation
-------------
Documentation is available at http://softlayer.github.io/softlayer-python/


Installation
------------
Install via pip:

.. code-block:: bash

	$ pip install softlayer


Or you can install from source. Download source and run:

.. code-block:: bash

	$ python setup.py install


The most up to date version of this library can be found on the SoftLayer
GitHub public repositories at http://github.com/softlayer. Please post to the
SoftLayer forums at http://forums.softlayer.com/ or open a support ticket in
the SoftLayer customer portal if you have any questions regarding use of this
library.


System Requirements
-------------------
* This library has been tested on Python 2.6, 2.7, 3.3 and 3.4.
* A valid SoftLayer API username and key are required to call SoftLayer's API.
* A connection to SoftLayer's private network is required to connect to
  SoftLayer’s private network API endpoints.


Copyright
---------
This software is Copyright (c) 2015 SoftLayer Technologies, Inc.

See the bundled LICENSE file for more information.
