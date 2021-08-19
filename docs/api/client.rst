.. _client:


API Documentation
=================
This is the primary API client to make API calls. It deals with constructing
and executing XML-RPC calls against the SoftLayer API. Below are some links
that will help to use the SoftLayer API.


* `SoftLayer API Documentation <https://softlayer.github.io/reference/softlayerapi/>`_
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
`getObject <https://sldn.softlayer.com/reference/services/SoftLayer_Account/getObject>`_
method on the
`SoftLayer_Account <https://sldn.softlayer.com/reference/services/SoftLayer_Account>`_
service.
::

    client.call('Account', 'getObject')

For a more complex example we'll retrieve a support ticket with id 123456 along
with the ticket's updates, the user it's assigned to, the servers attached to
it, and the datacenter those servers are in. To retrieve our extra information
using an `object mask <https://sldn.softlayer.com/article/object-masks/>`_.

Retrieve a ticket using object masks.
::

    ticket = client.call('Ticket', 'getObject',
        id=123456, mask="updates, assignedUser, attachedHardware.datacenter")


Now add an update to the ticket with `Ticket.addUpdate <https://sldn.softlayer.com/reference/services/SoftLayer_Ticket/addUpdate>`_.
This uses a parameter, which translate to positional arguments in the order
that they appear in the API docs.


::

    update = client.call('Ticket', 'addUpdate', {'entry' : 'Hello!'}, id=123456)

Let's get a listing of virtual guests using the domain example.com


::

    client.call('Account', 'getVirtualGuests',
        filter={'virtualGuests': {'domain': {'operation': 'example.com'}}})

This call gets tickets created between the beginning of March 1, 2013 and March 15, 2013.
More information on `Object Filters <https://sldn.softlayer.com/article/object-filters/>`_.

:NOTE: The `value` field for startDate and endDate is in `[]`, if you do not put the date in brackets the filter will not work.

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

    from pprint import pprint

    page1 = client.call('Account', 'getVirtualGuests', limit=10, offset=0)  # Page 1
    page2 = client.call('Account', 'getVirtualGuests', limit=10, offset=10)  # Page 2

    #Automatic Pagination (v5.5.3+), default limit is 100
    result = client.call('Account', 'getVirtualGuests', iter=True, limit=10)
    pprint(result)

    # Using a python generator, default limit is 100
    results = client.iter_call('Account', 'getVirtualGuests', limit=10)
    for result in results:
        pprint(result)

:NOTE: `client.call(iter=True)` will pull all results, then return. `client.iter_call()` will return a generator, and only make API calls as you iterate over the results. 

Here's how to create a new Cloud Compute Instance using
`SoftLayer_Virtual_Guest.createObject <https://sldn.softlayer.com/reference/services/SoftLayer_Virtual_Guest/createObject>`_.
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


Debugging
-------------
If you ever need to figure out what exact API call the client is making, you can do the following:

*NOTE* the `print_reproduceable` method produces different output for REST and XML-RPC endpoints. If you are using REST, this will produce a CURL call. IF you are using XML-RPC, it will produce some pure python code you can use outside of the SoftLayer library. 

::

    # Setup the client as usual
    client = SoftLayer.Client()
    # Create an instance of the DebugTransport, which logs API calls
    debugger = SoftLayer.DebugTransport(client.transport)
    # Set that as the default client transport
    client.transport = debugger
    # Make your API call
    client.call('Account', 'getObject')

    # Print out the reproduceable call
    for call in client.transport.get_last_calls():
        print(client.transport.print_reproduceable(call))


Dealing with KeyError Exceptions
--------------------------------

One of the pain points in dealing with the SoftLayer API can be handling issues where you expected a property to be returned, but none was.

The hostname property of a `SoftLayer_Billing_Item <https://sldn.softlayer.com/reference/datatypes/SoftLayer_Billing_Item/#hostname>`_ is a good example of this.

For example.

::
    
    # Uses default username and apikey from ~/.softlayer
    client = SoftLayer.create_client_from_env()
    # iter_call returns a python generator, and only makes another API call when the loop runs out of items.
    result = client.iter_call('Account', 'getAllBillingItems', iter=True, mask="mask[id,hostName]")
    print("Id, hostname")
    for item in result:
        # will throw a KeyError: 'hostName' exception on certain billing items that do not have a hostName
        print("{}, {}".format(item['id'], item['hostName']))

The Solution
^^^^^^^^^^^^

Using the python dictionary's `.get() <https://docs.python.org/3/library/stdtypes.html#dict.get>`_ is great for non-nested items.

::

    print("{}, {}".format(item.get('id'), item.get('hostName')))

Otherwise, this SDK provides a util function to do something similar. Each additional argument passed into `utils.lookup` will go one level deeper into the nested dictionary to find the item requested, returning `None` if a KeyError shows up.

::

    itemId = SoftLayer.utils.lookup(item, 'id')
    itemHostname = SoftLayer.utils.lookup(item, 'hostName')
    print("{}, {}".format(itemId, itemHostname))


API Reference
-------------

.. automodule:: SoftLayer
    :members:
    :ignore-module-all:

.. automodule:: SoftLayer.API
    :members:
    :ignore-module-all:

.. automodule:: SoftLayer.exceptions
    :members:     

.. automodule:: SoftLayer.decoration
    :members:
