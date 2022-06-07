SoftLayer API Python Client
===========================

This library is provided `as is` to make internal IMS API calls. You are responsible for your API usage, and any abuse, intentional or accidental, will result in your employee account being locked or limited.


Make sure you use the HTTPS url `https://internal.app0lb.dal10.softlayer.local/v3/internal/xmlrpc/`

Documentation
-------------
DThis project is based off the  `SLCLI <https://github.com/softlayer/softlayer-python>`_ , and most things that work there will work here.

There is no internal API documentation like SLDN.

Installation
------------
Install via pip:

.. code-block:: bash

	$ git clone https://github.ibm.com/SoftLayer/internal-softlayer-cli
  $ cd internal-softlayer-cli
  $ python setup.py install
  $ ./islcli login


Configuration
-------------

The config file is located at `~/.softlayer` or `~/AppData/Roaming/softlayer` for Windows systems.

Your config file should look something like this for using the islcli. Beware the `islcli` and `slcli` use the same config for the moment. You need to set `verify = False` in the config because the internal endpoint uses a self-signed SSL certificate.

.. code-block:: bash
  
  [softlayer]
  username = imsUsername
  verify = False
  endpoint_url = https://internal.app0lb.dal10.softlayer.local/v3/internal/xmlrpc/



Basic Usage
-----------

.. code-block:: bash

  $ islcli login
  $ islcli -a <account_id> vs list


Advanced Usage
--------------

You can automatically set some parameters via environment variables with by using the SLCLI prefix. For example

.. code-block:: bash

  $ export SLCLI_VERBOSE=3
  $ export SLCLI_FORMAT=json
  $ slcli -a <account_id> vs list

is equivalent to 

.. code-block:: bash

  $ slcli -vvv --format=json -a <account_id> vs list

Getting Help
------------

Feel free to open an issue if you think there is a bug, or a feature you want. Or asking in #sl-api on IBM slack. This is considered an unofficial project however, so questions might take some time to get answered.


Examples
--------

A curated list of examples on how to use this library can be found at `SLDN <https://softlayer.github.io/python/>`_


.. code-block:: python

  import SoftLayer
  client = SoftLayer.employee_client()
  username = input("Username:")
  password = input("Password:")
  yubikey = input("Yubi key:")
  client.authenticate_with_password(username, password, yubikey)
  result = client.call('SoftLayer_Account', 'getObject', id="12345", mask="mask[id]")


After logging in with `authenticate_with_password` the EmployeeClient will try to automatically refresh the login token when it gets a TokenExpired exception. It will also record the token in the config file for future use in the CLI.
  

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
          self.client = SoftLayer.EmployeeClient()
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
* Python 3.7, 3.8, or 3.9.
* A valid SoftLayer Employee  API username, password, Yubi Key
* A connection to SoftLayer's Employee VPN 

Python 2.7 Support
------------------
Python 2.7 is  `End Of Life as of 2020 <https://www.python.org/dev/peps/pep-0373/>`_ . Its not supported, you will need to upgrade to python 3.7 at least.


Python Packages
---------------
* prettytable >= 2.0.0
* click >= 7
* requests >= 2.20.0
* prompt_toolkit >= 2
* pygments >= 2.0.0
* urllib3 >= 1.24
* Rich

Copyright
---------
This software is Copyright (c) 2016-2021 SoftLayer Technologies, Inc.

See the bundled LICENSE file for more information.
