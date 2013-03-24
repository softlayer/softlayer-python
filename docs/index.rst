.. SoftLayer API Python Client documentation

SoftLayer API Python Client
===========================
This is the documentation to SoftLayer's Python API Bindings. These bindings use SoftLayer's `XML-RPC interface <http://sldn.softlayer.com/article/XML-RPC>`_ in order to manage SoftLayer services.

Release v\ |version|. (:ref:`Installation <install>`)

API Documentation
-----------------
.. toctree::
   :maxdepth: 2

   install
   api/client

::

	>>> import SoftLayer
	>>> client = SoftLayer.Client(username="username", api_key="api_key")
	>>> resp = client['Account'].getObject()
	>>> resp['companyName']
	'Your Company'

Managers
--------
Managers mask out a lot of the complexities of using the API into classes that provide a simpler interface to various services.

.. toctree::
   :maxdepth: 1
   :glob:

   api/managers/*

::

	>>> from SoftLayer.CCI import CCIManager
	>>> cci = CCIManager(client)
	>>> cci.list_instances()
	[...]

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

