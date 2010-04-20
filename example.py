# Copyright (c) 2010, SoftLayer Technologies, Inc. All rights reserved.
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
import SoftLayer.API

# Used for pretty printing output.
import pprint

# It's possible to define your SoftLayer API username and key diredtly in the
# package, but it's far easier to define them before creating your API client.
api_username = 'set me'
api_key = 'set me too'

# Usage:
# SoftLayer.API.Client([API Service], <object id>, [username], [API key])
#
# API Service: The name of the API service you wish to connect to.
# id:          An optional id to initialize your API service with, if you're
#              interacting with a specific object. If you don't need to specify
#              an id then pass None to the client.
# username:    Your SoftLayer API username.
# API key:     Your SoftLayer API key,
client = SoftLayer.API.Client('SoftLayer_Account', None, api_username, api_key)

# Once your client object is created you can call API methods for that service
# directly against your client object. A call may throw an exception on error,
# so it's best to try your call and catch exceptions.
#
# This example calls the getObject() method in the SoftLayer_Account API
# service. <http://sldn.softlayer.com/wiki/index.php/SoftLayer_Account::getObject>
# It retrieved basic account information, and is a great way to test your API
# account and connectivity.
#
# If you're using Python 3.x then you'll need to change these except and
# print() statements accordingly.
try:
    pprint.pprint(client.getObject())
except Exception, e:
    print e
