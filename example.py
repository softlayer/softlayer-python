#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    example
    ~~~~~~~
    This is an example of using the SoftLayer API Python Client.

    For more examples and documentation, refer to:
    	https://softlayer-api-python-client.readthedocs.org

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
# The SoftLayer API client package is here:
import SoftLayer
import pprint

# Usage:
# SoftLayer.Client(username=[Username], api_key=[API key])
#
# Username:    Your SoftLayer API username.
# API key:     Your SoftLayer API key,
username = 'SET ME'
api_key = 'SET ME'

client = SoftLayer.Client(username=username, api_key=api_key)

# Once your client object is created you can call API methods for that service
# directly against your client object. Each call may throw an raise a
# SoftLayerError exception.
#
# This example calls the getObject() method in the SoftLayer_Account API
# service. <http://sldn.softlayer.com/wiki/index.php/SoftLayer_Account::getObject>
# It retrieves basic account information, and is a great way to test your API
# account and connectivity.
pprint.pprint(client['Account'].getObject())

# For a more complex example we’ll retrieve a support ticket with id 123456
# along with the ticket’s updates, the user it’s assigned to, the servers
# attached to it, and the datacenter those servers are in. We’ll retrieve our
# extra information using a nested object mask. After we have the ticket we’ll
# update it with the text ‘Hello!’.

# Retrieve the ticket record.
ticket = client['Ticket'].getObject(
	id=123456, mask='updates,assignedUser,attachedHardware.datacenter')
pprint.pprint(ticket)

# Now update the ticket.
update = client['Ticket'].addUpdate(id=123456, {'entry': 'Hello!'})
pprint.pprint(update)
