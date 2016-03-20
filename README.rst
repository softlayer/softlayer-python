SoftLayer API Python Client
===========================
.. image:: https://travis-ci.org/softlayer/softlayer-python.svg?branch=master
    :target: https://travis-ci.org/softlayer/softlayer-python

.. image:: https://landscape.io/github/softlayer/softlayer-python/master/landscape.svg
    :target: https://landscape.io/github/softlayer/softlayer-python/master

.. image:: https://badge.fury.io/py/SoftLayer.svg
    :target: http://badge.fury.io/py/SoftLayer

.. image:: https://coveralls.io/repos/softlayer/softlayer-python/badge.svg
    :target: https://coveralls.io/r/softlayer/softlayer-python


This library provides a simple Python client to interact with `SoftLayer's
XML-RPC API <http://developer.softlayer.com/reference/softlayerapi>`_.

A command-line interface is also included and can be used to manage various
SoftLayer products and services.


Documentation
-------------
Documentation for the Python client is available at
http://softlayer.github.io/softlayer-python/.

Additional API documentation can be found on the SoftLayer Development Network:

* `SoftLayer API reference
  <http://developer.softlayer.com/reference/softlayerapi>`_
* `Object mask information and examples
  <http://developer.softlayer.com/article/Object-Masks>`_

Installation
------------
Install via pip:

.. code-block:: bash

	$ pip install softlayer


Or you can install from source. Download source and run:

.. code-block:: bash

	$ python setup.py install


The most up-to-date version of this library can be found on the SoftLayer
GitHub public repositories at http://github.com/softlayer. Please post to Stack Overflow at https://stackoverflow.com/ or open a support ticket in the customer portal if you have any questions regarding use of this library. If you use Stack Overflow please tag your posts with “SoftLayer” so our team can easily find your post. 

InsecurePlatformWarning Notice
------------------------------
This library relies on the `requests <http://docs.python-requests.org/>`_ library to make HTTP requests. On Python versions below Python 2.7.9, requests has started emitting a security warning (InsecurePlatformWarning) due to insecurities with creating SSL connections. To resolve this, upgrade to Python 2.7.9+ or follow the instructions here: http://stackoverflow.com/a/29099439.

System Requirements
-------------------
* Python 2.7, 3.3 or higher.
* A valid SoftLayer API username and key.
* A connection to SoftLayer's private network is required to use
  our private network API endpoints.


Copyright
---------
This software is Copyright (c) 2016 SoftLayer Technologies, Inc.

See the bundled LICENSE file for more information.
