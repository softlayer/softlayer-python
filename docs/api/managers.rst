.. _managers:

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

   managers/*