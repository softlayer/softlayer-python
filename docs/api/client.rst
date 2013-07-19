.. _client:


Developer Interface
===================
This is the primary API client to make API calls. It deals with constructing and executing XML-RPC calls against the SoftLayer API.

Getting Started
---------------
You can pass in your username and api_key when creating a SoftLayer client instance. However, you can set these in the environmental variables 'SL_USERNAME' and 'SL_API_KEY'

Creating a client instance by passing in the username/api_key:
::

    import SoftLayer
    client = SoftLayer.Client(username='YOUR_USERNAME', api_key='YOUR_API_KEY')

Creating a client instance with environmental variables set:
::

    # env variables
    # SL_USERNAME = YOUR_USERNAME
    # SL_API_KEY = YOUR_API_KEY
    import SoftLayer
    client = SoftLayer.Client()

Below is an example of creating a client instance with more options. This will create a client with the private API endpoint (only accessable from the SoftLayer network), a timeout of 2 minutes, and with verbose mode on (prints out more than you ever wanted to know about the HTTP requests to stdout).
::

    client = SoftLayer.Client(
            username='YOUR_USERNAME',
            api_key='YOUR_API_KEY'
            endpoint_url=SoftLayer.API_PRIVATE_ENDPOINT,
            timeout=240,
            verbose=True,
        )

Making API Calls
----------------
The SoftLayer API client for python leverages SoftLayer's XML-RPC API. It supports authentication, object masks, object filters, limits, offsets, and retrieving objects by id. The following section assumes you have a initialized client named 'client'.

The best way to test our setup is to call the `getObject <http://sldn.softlayer.com/reference/services/SoftLayer_Account/getObject>`_ method on the `SoftLayer_Account <http://sldn.softlayer.com/reference/services/SoftLayer_Account>`_ service.
::

    client['Account'].getObject()

For a more complex example we'll retrieve a support ticket with id 123456 along with the ticket's updates, the user it's assigned to, the servers attached to it, and the datacenter those servers are in. To retrieve our extra information using an `object mask <http://sldn.softlayer.com/article/Extended-Object-Masks>`_.

Retreive a ticket using Object Masks.
::

    ticket = client['Ticket'].getObject(
        id=123456, mask="mask[updates, assignedUser, attachedHardware.datacenter]")


Now add an update to the ticket with `Ticket.addUpdate <http://sldn.softlayer.com/reference/services/SoftLayer_Ticket/addUpdate>`_. This uses a parameter, which translate to positional arguments in the order that they appear in the API docs.
::

    update = client['Ticket'].addUpdate({'entry' : 'Hello!'}, id=123456)

Let's get a listing of virtual guests using the domain example.com
::

    client['Account'].getVirtualGuests(
        filter={'virtualGuests': {'domain': {'operation': 'example.com'}}})

This call gets tickets created between the beginning of March 1, 2013 and March 15, 2013.
::

    client['Account'].getTickets(
        filter={
            'tickets': {
                'createDate': {
                    'operation': 'betweenDate',
                    'options': [
                        {'name': 'startDate', 'value': ['03/01/2013 0:0:0']},
                        {'name': 'endDate', 'value': ['03/15/2013 23:59:59']}
                    ]
                }
            }
        }
    )

SoftLayer's XML-RPC API also allows for pagination.
::

    client['Account'].getVirtualGuests(limit=10, offset=0)  # Page 1
    client['Account'].getVirtualGuests(limit=10, offset=10)  # Page 2

Here's how to create a new Cloud Compute Instance using `SoftLayer_Virtual_Guest.createObject <http://sldn.softlayer.com/reference/services/SoftLayer_Virtual_Guest/createObject>`_. Be warned, this call actually creates an hourly CCI so this does have billing implications.
::

    client['Virtual_Guest'].createObject({
            'hostname': 'myhostname',
            'domain': 'example.com',
            'startCpus': 1,
            'maxMemory': 1024,
            'hourlyBillingFlag': 'true',
            'operatingSystemReferenceCode': 'UBUNTU_LATEST',
            'localDiskFlag': 'false'
        })


API Reference
-------------
.. autoclass:: SoftLayer.Client
   :members:
   :undoc-members:

   .. automethod:: SoftLayer.Client.__getitem__

.. autoclass:: SoftLayer.API.Service
   :members:
   :undoc-members:

   .. automethod:: SoftLayer.API.Service.__call__


.. automodule:: SoftLayer.exceptions
   :members:
   :undoc-members:


Backwards Compatibility
-----------------------
If you've been using the older Python client (<2.0), you'll be happy to know that the old API is still currently working. However, you should deprecate use of the old stuff. Below is an example of the old API converted to the new one.

.. automodule:: SoftLayer.deprecated
   :members:
   :undoc-members:

::

	import SoftLayer.API
	client = SoftLayer.API.Client('SoftLayer_Account', None, 'username', 'api_key')
	client.set_object_mask({'ipAddresses' : None})
	client.set_result_limit(10, offset=10)
	client.getObject()

... changes to ...
::

	import SoftLayer
	client = SoftLayer.Client(username='username', api_key='api_key')
	client['Account'].getObject(mask="mask[ipAddresses]", limit=10, offset=0)

Deprecated APIs
^^^^^^^^^^^^^^^
Below are examples of how the old usages to the new API.

**Importing the module**
::

	# Old
	import SoftLayer.API

	# New
	import SoftLayer

**Creating a client instance**
::

	# Old
	client = SoftLayer.API.Client('SoftLayer_Account', None, 'username', 'api_key')

	# New
	client = SoftLayer.Client(username='username', api_key='api_key')
	service = client['Account']

**Making an API call**
::

	# Old
	client = SoftLayer.API.Client('SoftLayer_Account', None, 'username', 'api_key')
	client.getObject()

	# New
	client = SoftLayer.Client(username='username', api_key='api_key')
	client['Account'].getObject()

	# Optionally
	service = client['Account']
	service.getObject()

**Setting Object Mask**
::

	# Old
	client.set_object_mask({'ipAddresses' : None})

	# New
	client['Account'].getObject(mask="mask[ipAddresses]")

**Using Init Parameter**
::

	# Old
	client.set_init_parameter(1234)

	# New
	client['Account'].getObject(id=1234)

**Setting Result Limit and Offset**
::

	# Old
	client.set_result_limit(10, offset=10)

	# New
	client['Account'].getObject(limit=10, offset=10)

**Adding Additional Headers**
::

	# Old
	# These headers are persisted accross API calls
	client.add_header('header', 'value')

	# New
	# These headers are NOT persisted accross API calls
	client['Account'].getObject(headers={'header': 'value'})

**Removing Additional Headers**
::

	# Old
	client.remove_header('header')

	# New
	client['Account'].getObject()

**Adding Additional HTTP Headers**
::

	# Old
	client.add_raw_header('header', 'value')

	# New
	client['Account'].getObject(raw_headers={'header': 'value'})

**Changing Authentication Credentials**
::

	# Old
	client.set_authentication('username', 'api_key')

	# New
	client.username = 'username'
	client.api_key = 'api_key'
