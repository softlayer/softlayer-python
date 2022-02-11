SoftLayer API Python Client
===========================
.. image:: https://github.com/softlayer/softlayer-python/workflows/Tests/badge.svg
    :target: https://github.com/softlayer/softlayer-python/actions?query=workflow%3ATests

.. image:: https://github.com/softlayer/softlayer-python/workflows/documentation/badge.svg
    :target: https://github.com/softlayer/softlayer-python/actions?query=workflow%3Adocumentation

.. image:: https://landscape.io/github/softlayer/softlayer-python/master/landscape.svg
    :target: https://landscape.io/github/softlayer/softlayer-python/master

.. image:: https://badge.fury.io/py/SoftLayer.svg
    :target: http://badge.fury.io/py/SoftLayer

.. image:: https://coveralls.io/repos/github/softlayer/softlayer-python/badge.svg?branch=master
    :target: https://coveralls.io/github/softlayer/softlayer-python?branch=master

.. image:: https://snapcraft.io//slcli/badge.svg
    :target: https://snapcraft.io/slcli


This library provides a simple Python client to interact with `SoftLayer's
XML-RPC API <https://softlayer.github.io/reference/softlayerapi>`_.

A command-line interface is also included and can be used to manage various
SoftLayer products and services.


Documentation
-------------
Documentation for the Python client is available at `Read the Docs <https://softlayer-python.readthedocs.io/en/latest/index.html>`_ .

Additional API documentation can be found on the SoftLayer Development Network:

* `SoftLayer API reference
  <https://sldn.softlayer.com/reference/softlayerapi>`_
* `Object mask information and examples
  <https://sldn.softlayer.com/article/object-masks>`_
* `Code Examples
  <https://sldn.softlayer.com/python/>`_

Installation
------------
Install via pip:

.. code-block:: bash

	$ pip install softlayer


Or you can install from source. Download source and run:

.. code-block:: bash

	$ python setup.py install

Another (safer) method of installation is to use the published snap. Snaps are available for any Linux OS running snapd, the service that runs and manage snaps. Snaps are "auto-updating" packages and will not disrupt the current versions of libraries and software packages on your Linux-based system. To learn more, please visit: https://snapcraft.io/ 

To install the slcli snap:

.. code-block:: bash

	$ sudo snap install slcli 
	
	(or to get the latest release)
	
	$ sudo snap install slcli --edge
	
	


The most up-to-date version of this library can be found on the SoftLayer
GitHub public repositories at http://github.com/softlayer. For questions regarding the use of this library please post to Stack Overflow at https://stackoverflow.com/ and  your posts with “SoftLayer” so our team can easily find your post. To report a bug with this library please create an Issue on github.

InsecurePlatformWarning Notice
------------------------------
This library relies on the `requests <http://docs.python-requests.org/>`_ library to make HTTP requests. On Python versions below Python 2.7.9, requests has started emitting a security warning (InsecurePlatformWarning) due to insecurities with creating SSL connections. To resolve this, upgrade to Python 2.7.9+ or follow the instructions here: http://stackoverflow.com/a/29099439.

Basic Usage
-----------

- `The Complete Command Directory <https://softlayer-python.readthedocs.io/en/latest/cli_directory/>`_

Advanced Usage
--------------

You can automatically set some parameters via environment variables with by using the SLCLI prefix. For example

.. code-block:: bash

  $ export SLCLI_VERBOSE=3
  $ export SLCLI_FORMAT=json
  $ slcli vs list

is equivalent to 

.. code-block:: bash

  $ slcli -vvv --format=json vs list

Getting Help
------------
Bugs and feature requests about this library should have a `GitHub issue <https://github.com/softlayer/softlayer-python/issues>`_ opened about them. 

Issues with the Softlayer API itself should be addressed by opening a ticket.


Examples
--------

A curated list of examples on how to use this library can be found at `SLDN <https://softlayer.github.io/python/>`_

Debugging
---------
To get the exact API call that this library makes, you can do the following.

For the CLI, just use the -vvv option. If you are using the REST endpoint, this will print out a curl command that you can use, if using XML, this will print the minimal python code to make the request without the softlayer library.

.. code-block:: bash

  $ slcli -vvv vs list


If you are using the library directly in python, you can do something like this.

.. code-block:: python

  import SoftLayer
  import logging

  class invoices():

      def __init__(self):
          self.client = SoftLayer.Client()
          debugger = SoftLayer.DebugTransport(self.client.transport)
          self.client.transport = debugger

      def main(self):
          mask = "mask[id]"
          account = self.client.call('Account', 'getObject', mask=mask);
          print("AccountID: %s" % account['id'])

      def debug(self):
          for call in self.client.transport.get_last_calls():
              print(self.client.transport.print_reproduceable(call))

  if __name__ == "__main__":
      main = example()
      main.main()
      main.debug()



System Requirements
-------------------
* Python 3.5, 3.6, 3.7, 3.8, or 3.9.
* A valid SoftLayer API username and key.
* A connection to SoftLayer's private network is required to use
  our private network API endpoints.

Python 2.7 Support
------------------
As of version 5.8.0 SoftLayer-Python will no longer support python2.7, which is `End Of Life as of 2020 <https://www.python.org/dev/peps/pep-0373/>`_ .
If you cannot install python 3.6+ for some reason, you will need to use a version of softlayer-python <= 5.7.2



Python Packages
---------------
* prettytable >= 2.0.0
* click >= 7
* requests >= 2.20.0
* prompt_toolkit >= 2
* pygments >= 2.0.0
* urllib3 >= 1.24

Copyright
---------
This software is Copyright (c) 2016-2021 SoftLayer Technologies, Inc.

See the bundled LICENSE file for more information.
