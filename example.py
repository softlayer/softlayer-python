#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * Neither SoftLayer Technologies, Inc. nor the names of its contributors may
#    be used to endorse or promote products derived from this software without
#    specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# The SoftLayer API client package is here:
import SoftLayer
import pprint

# Usage:
# SoftLayer.Client(username=[username], api_key=[API key])
#
# username:    Your SoftLayer API username.
# API key:     Your SoftLayer API key,
client = SoftLayer.Client(username=api_username, api_key=api_key)

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
ticket = client['Ticket'].getObject(id=123456,
    mask={
        'updates' : None,
        'assignedUser' : None,
        'attachedHardware' : {
            'datacenter' : None
        },
    })
pprint.pprint(ticket)

# Now update the ticket.
update = client['Ticket'].addUpdate(id=123456, {'entry' : 'Hello!'})
pprint.pprint(update)
