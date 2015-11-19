.. _client:


API Documentation
=================
This is the primary API client to make API calls. It deals with constructing
and executing XML-RPC calls against the SoftLayer API. Below are some links
that will help to use the SoftLayer API.


* `SoftLayer API Documentation <http://developer.softlayer.com/reference/softlayerapi>`_
* `Source on GitHub <https://github.com/softlayer/softlayer-python>`_

::

	>>> import SoftLayer
	>>> client = SoftLayer.create_client_from_env(username="username", api_key="api_key")
	>>> resp = client.call('Account', 'getObject')
	>>> resp['companyName']
	'Your Company'


Getting Started
---------------
You can pass in your username and api_key when creating a SoftLayer client
instance. However, you can also set these in the environmental variables
'SL_USERNAME' and 'SL_API_KEY'.

Creating a client instance by passing in the username/api_key:
::

    import SoftLayer
    client = SoftLayer.create_client_from_env(username='YOUR_USERNAME', api_key='YOUR_API_KEY')

Creating a client instance with environmental variables set:
::

    $ export SL_USERNAME=YOUR_USERNAME
    $ export SL_API_KEY=YOUR_API_KEY
    $ python
    >>> import SoftLayer
    >>> client = SoftLayer.create_client_from_env()

Below is an example of creating a client instance with more options. This will
create a client with the private API endpoint (only accessible from the
SoftLayer private network) and a timeout of 4 minutes.
::

    client = SoftLayer.create_client_from_env(username='YOUR_USERNAME',
                                              api_key='YOUR_API_KEY'
                                              endpoint_url=SoftLayer.API_PRIVATE_ENDPOINT,
                                              timeout=240)

Managers
--------
For day-to-day operation, most users will find the managers to be the most
convenient means for interacting with the API. Managers abstract a lot of the
complexities of using the API into classes that provide a simpler interface to
various services. These are higher-level interfaces to the SoftLayer API.
::

	from SoftLayer import VSManager, Client
	client = Client(...)
	vs = VSManager(client)
	vs.list_instances()
	[...]

**Available managers**:

.. toctree::
   :maxdepth: 1
   :glob:

   managers/*

If you need more power or functionality than the managers provide, you can
make direct API calls as well.


Making API Calls
----------------
For full control over your account and services, you can directly call the
SoftLayer API. The SoftLayer API client for python leverages SoftLayer's
XML-RPC API. It supports authentication, object masks, object filters, limits,
offsets, and retrieving objects by id. The following section assumes you have
an initialized client named 'client'.

The best way to test our setup is to call the
`getObject <http://developer.softlayer.com/reference/services/SoftLayer_Account/getObject>`_
method on the
`SoftLayer_Account <http://developer.softlayer.com/reference/services/SoftLayer_Account>`_
service.
::

    client.call('Account', 'getObject')

For a more complex example we'll retrieve a support ticket with id 123456 along
with the ticket's updates, the user it's assigned to, the servers attached to
it, and the datacenter those servers are in. To retrieve our extra information
using an `object mask <http://developer.softlayer.com/article/Extended-Object-Masks>`_.

Retrieve a ticket using object masks.
::

    ticket = client.call('Ticket', 'getObject',
        id=123456, mask="updates, assignedUser, attachedHardware.datacenter")


Now add an update to the ticket with
`Ticket.addUpdate <http://developer.softlayer.com/reference/services/SoftLayer_Ticket/addUpdate>`_.
This uses a parameter, which translate to positional arguments in the order
that they appear in the API docs.
::

    update = client.call('Ticket', 'addUpdate', {'entry' : 'Hello!'}, id=123456)

Let's get a listing of virtual guests using the domain example.com
::

    client.call('Account', 'getVirtualGuests',
        filter={'virtualGuests': {'domain': {'operation': 'example.com'}}})

This call gets tickets created between the beginning of March 1, 2013 and
March 15, 2013.
::

    client.call('Account', 'getTickets',
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

    client.call('Account', 'getVirtualGuests', limit=10, offset=0)  # Page 1
    client.call('Account', 'getVirtualGuests', limit=10, offset=10)  # Page 2

Here's how to create a new Cloud Compute Instance using
`SoftLayer_Virtual_Guest.createObject <http://developer.softlayer.com/reference/services/SoftLayer_Virtual_Guest/createObject>`_.
Be warned, this call actually creates an hourly virtual server so this will
have billing implications.
::

    client.call('Virtual_Guest', 'createObject', {
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

.. automodule:: SoftLayer
	:members:
