.. SoftLayer API Python Client documentation

SoftLayer API Python Client
===========================
This is the documentation to SoftLayer's Python API Bindings. These bindings use SoftLayer's `XML-RPC interface <http://sldn.softlayer.com/article/XML-RPC>`_ in order to manage SoftLayer services.

Release v\ |version|. (:ref:`Installation <install>`)

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

   install
   api/client


Managers
--------
::

	>>> from SoftLayer.CCI import CCIManager
	>>> cci = CCIManager(client)
	>>> cci.list_instances()
	[...]

Managers mask out a lot of the complexities of using the API into classes that provide a simpler interface to various services.

.. toctree::
   :maxdepth: 1
   :glob:

   api/managers/*


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
   cli/dev

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

