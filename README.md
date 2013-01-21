SoftLayer API Python Client
===========================
[![Build Status](https://travis-ci.org/sudorandom/softlayer-api-python-client.png)](https://travis-ci.org/softlayer/softlayer-api-python-client)

This code provides a simple Python library to use the [SoftLayer API](http://sldn.softlayer.com/reference/softlayerapi).

Overview
--------

This library provides a simple interface to interact with SoftLayer's XML-RPC API and provides support for many of SoftLayer API's features like [object masks](http://sldn.softlayer.com/article/Using-Object-Masks-SoftLayer-API).

Installation
------------
Install via pip:
```
pip install softlayer
```

Or you can install from source. Download source and run:

```
python setup.py install
```


The most up to date version of this library can be found on the SoftLayer github public repositories: http://github.com/softlayer. Please post to the SoftLayer forums http://forums.softlayer.com/ or open a support ticket in the SoftLayer customer portal if you have any questions regarding use of this library.

System Requirements
-------------------

* This library has been tested on Python 2.5, 2.6, 2.7, 3.2 and 3.3.
* A valid SoftLayer API username and key are required to call SoftLayer's API
* A connection to SoftLayer's private network is required to connect to SoftLayer’s private network API endpoints.

## Getting Started
You can pass in your username and api_key when creating a SoftLayer client instance. However, you can set these in the environmental variables 'SL_USERNAME' and 'SL_API_KEY'

Here's a simple usage example that retrieves account information by calling the [getObject](http://sldn.softlayer.com/wiki/index.php/SoftLayer_Account::getObject) method on the [SoftLayer_Account](http://sldn.softlayer.com/wiki/index.php/SoftLayer_Account) service.

Creating a client instance
```
import SoftLayer
client = SoftLayer.Client(username='YOUR_USERNAME', api_key='YOUR_API_KEY')
```

Creating a client instance with more options. This will create a client with the private API endpoint (only accessable from the SoftLayer network), a timeout of 2 minutes, and with verbose mode on (prints out more than you ever wanted to know about the HTTP requests to stdout).
```
client = SoftLayer.Client(
        username='YOUR_USERNAME',
        api_key='YOUR_API_KEY'
        endpoint_url=SoftLayer.API_PRIVATE_ENDPOINT,
        timeout=240,
        verbose=True,
    )
```

Okay, we have a client. Let's do something with it. The best API call to make is 
```
client['Account'].getObject()
```

For a more complex example we'll retrieve a support ticket with id 123456 along with the ticket's updates, the user it's assigned to, the servers attached to it, and the datacenter those servers are in. We'll retrieve our extra information using a nested object mask.

Retreive a ticket using Object Masks.
```
ticket = client['Ticket'].getObject(id=123456,
    mask={
        'updates' : None,
        'assignedUser' : None,
        'attachedHardware' : {
            'datacenter' : None
        },
    })
```

Now add an update to the ticket.
```
update = client['Ticket'].addUpdate({'entry' : 'Hello!'}, id=123456)
```

Let's get a listing of virtual guests using the domain example.com
```
client['Account'].getVirtualGuests(
    filter={'virtualGuests': {'domain': 'example.com'}})
```

SoftLayer's XML-RPC API also allows for pagination.
```
client['Account'].getVirtualGuests(limit=10, offset=0)  # Page 1
client['Account'].getVirtualGuests(limit=10, offset=10)  # Page 2
```

Here's how to create a new [Cloud Compute Instance](http://sldn.softlayer.com/blog/phil/Simplified-CCI-Creation). Be warned, this call actually creates an hourly CCI so this does have billing implications.
```
client['Virtual_Guest'].createObject({
        'hostname': 'myhostname',
        'domain': 'example.com',
        'startCpus': 1,
        'maxMemory': 1024,
        'hourlyBillingFlag': 'true',
        'operatingSystemReferenceCode': 'UBUNTU_LATEST',
        'localDiskFlag': 'false'
    })
```

Backwards Compatability
-----------------------
If you've been using the older Python client, you'll be happy to know that the old API is still currently working. However, you should deprecate use of the old stuff. Below is an example of the old API converted to the new one.
```python
import SoftLayer.API
client = SoftLayer.API.Client('SoftLayer_Account', None, 'username', 'api_key')
client.set_object_mask({...})
client.set_result_limit(10, offset=0)
client.getObject()
```
changes to 
```python
import SoftLayer
client = SoftLayer.Client(username='username', api_key='api_key')
client['Account'].getObject(mask={..}, limit=10, offset=0)
```

### Deprecated APIs
* SoftLayer.API.Client.__init__ parameters: service_name, id => SoftLayer.API.Client['SERVICE'].METHOD(id=...)
* SoftLayer.API.Client.add_header() => SoftLayer.API.Client['SERVICE'].METHOD(headers={...})
* SoftLayer.API.Client.remove_header() => SoftLayer.API.Client['SERVICE'].METHOD(headers={...})
* SoftLayer.API.Client.set_authentication() => _
* SoftLayer.API.Client.set_init_parameter() => SoftLayer.API.Client['SERVICE'].METHOD(id=...)
* SoftLayer.API.Client.set_object_mask() => SoftLayer.API.Client['SERVICE'].METHOD(mask={...})
* SoftLayer.API.Client.set_result_limit() => SoftLayer.API.Client['SERVICE'].METHOD(limit=..., offset=...)
* SoftLayer.API.Client.METHOD() => SoftLayer.API.Client['SERVICE'].METHOD()


Copyright
---------
This software is Copyright (c) 2013 [SoftLayer Technologies, Inc](http://www.softlayer.com/). See the bundled LICENSE file for more information.
