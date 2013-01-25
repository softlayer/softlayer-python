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
"""
SoftLayer Python API Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~
A library to contact SoftLayer's backend services through the XML-RPC interface
See U{http://sldn.softlayer.com/article/Python}


usage:

    >>> import SoftLayer
    >>> client = SoftLayer.Client(username="username", api_key="api_key")
    >>> resp = client['SoftLayer_Account'].getObject()
    >>> resp['companyName']
    'Your Company'

"""
from SoftLayer.consts import VERSION

__title__ = 'SoftLayer'
__version__ = VERSION
__author__ = 'SoftLayer Technologies, Inc.'
__license__ = 'The BSD License'
__copyright__ = 'Copyright 2013 SoftLayer Technologies, Inc.'
__all__ = ['Client', 'SoftLayerError', 'API_PUBLIC_ENDPOINT',
           'API_PRIVATE_ENDPOINT']

from API import Client, API_PUBLIC_ENDPOINT, API_PRIVATE_ENDPOINT
from SoftLayer.exceptions import SoftLayerError
