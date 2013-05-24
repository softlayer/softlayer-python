.. _managers:

Managers
--------
::

	>>> from SoftLayer import CCIManager, Client
	>>> client = Client(...)
	>>> cci = CCIManager(client)
	>>> cci.list_instances()
	[...]

Managers mask out a lot of the complexities of using the API into classes that provide a simpler interface to various services. These are higher-level interfaces to the SoftLayer API.

.. toctree::
   :maxdepth: 1
   :glob:

   managers/*