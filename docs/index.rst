.. SoftLayer API Python Client documentation

SoftLayer API Python Client |version|
========================================
This is the documentation to SoftLayer's Python API Bindings. These bindings use SoftLayer's `XML-RPC interface <http://sldn.softlayer.com/article/XML-RPC>`_ in order to manage SoftLayer services.

.. toctree::
   :maxdepth: 2

   install
   SoftLayer API Documentation <http://sldn.softlayer.com/reference/softlayerapi>
   Source on Github <https://github.com/softlayer/softlayer-api-python-client>
   SoftLayer Developer Network <http://sldn.softlayer.com/>
   Twitter <https://twitter.com/SoftLayerDevs>


API Documentation
-----------------
::

	>>> import SoftLayer
	>>> client = SoftLayer.Client(username="username", api_key="api_key")
	>>> resp = client['Account'].getObject()
	>>> resp['companyName']
	'Your Company'

.. toctree::
   :maxdepth: 2

   api/client
   api/managers


Command-Line Interface
----------------------
::

	$ sl cci list
	:.........:............:....................:.......:........:................:..............:....................:
	:    id   : datacenter :       host         : cores : memory :   primary_ip   :  backend_ip  : active_transaction :
	:.........:............:....................:.......:........:................:..............:....................:
	: 1234567 :   dal05    :  test.example.com  :   4   :   4G   :    12.34.56    :   65.43.21   :         -          :
	:.........:............:....................:.......:........:................:..............:....................:

.. toctree::
   :maxdepth: 2

   cli
   cli/cci
   cli/dev


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

