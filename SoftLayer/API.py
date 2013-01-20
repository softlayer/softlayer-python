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
SoftLayer API bindings

See U{http://sldn.softlayer.com/article/Python}
"""

from urlparse import urlparse
import socket
import xmlrpclib
import os

API_USERNAME = None
API_KEY = None
API_PUBLIC_ENDPOINT = 'https://api.softlayer.com/xmlrpc/v3/'
API_PRIVATE_ENDPOINT = 'https://api.service.softlayer.com/xmlrpc/v3/'
API_BASE_URL = API_PUBLIC_ENDPOINT


class SoftLayerError(Exception):
    pass


class Client:
    """A SoftLayer API client
    Clients are intended to be declared once per service and used for all calls
    made to that service.

    :param service_name: The name of the SoftLayer API service to query.
    :param id: An optional object if if you're instantiating a particular
        SoftLayer_API object. Setting an id defines this client's
        initialization parameter.
    :param username: An optional API username if you wish to bypass the
        package's built-in username.
    :param api_key: An optional API key if you wish to bypass the package's
        built in API key.
    :param endpoint_url: The API endpoint base URL you wish to connect to.
        Set this to API_PRIVATE_ENDPOINT to connect via SoftLayer's private
        network.
    :param timeout: Timeout for API requests
    :param verbose: When true, prints details about every HTTP request.

    Usage::

        >>> import SoftLayer
        >>> client = SoftLayer.Client(username="username", api_key="api_key")
        >>> resp = client['SoftLayer_Account'].getObject()
        >>> resp['companyName']
        'Your Company'

    """
    _prefix = "SoftLayer_"

    def __init__(self, service_name=None, id=None, username=None, api_key=None,
                 endpoint_url=None, timeout=0, verbose=False):
        self.verbose = verbose
        self._service_name = service_name
        self._headers = {}
        self._raw_headers = {}

        self.username = username or API_USERNAME or os.environ.get('SL_USERNAME')
        self.api_key = api_key or API_KEY or os.environ.get('SL_API_KEY')

        if not all((self.username, self.api_key)):
            raise SoftLayerError(
                'Must supply username, api_key and service_name')

        self.set_authentication(self.username, self.api_key)

        if id is not None:
            self.set_init_parameter(int(id))

        self._endpoint_url = (endpoint_url or API_BASE_URL or \
            API_PUBLIC_ENDPOINT).rstrip('/')
        http_protocol = urlparse(self._endpoint_url).scheme

        if http_protocol == "https":
            self.transport = SecureProxyTransport()
        else:
            self.transport = ProxyTransport()

        self._timeout = timeout

    def add_raw_header(self, name, value):
        self._raw_headers[name] = value

    def add_header(self, name, value):
        """ Set a SoftLayer API call header [deprecated]

        :param name: The name of the header to add
        :param value: The header to add.
        """
        name = name.strip()

        if name is None or name is '':
            raise SoftLayerError('Please specify a header name.')

        self._headers[name] = value

    def remove_header(self, name):
        """ Remove a SoftLayer API call header [deprecated]

        :param name: The name of the header to remove.
        """

        if name in self._headers:
            del self._headers[name.strip()]

    def set_authentication(self, username, api_key):
        """ Set user and key to authenticate a SoftLayer API call [deprecated]

        Use this method if you wish to bypass the API_USER and API_KEY class
        constants and set custom authentication per API call.

        See U{https://manage.softlayer.com/Administrative/apiKeychain} for more
        information.

        :param username: The username to authenticate an API call.
        :param api_key: The user's API key.
        """

        self.add_header('authenticate', {
            'username': username.strip(),
            'apiKey': api_key.strip(),
        })

    def set_init_parameter(self, id):
        """ Set an initialization parameter header [deprecated]

        Initialization parameters instantiate a SoftLayer API service object to
        act upon during your API method call. For instance, if your account has
        a server with id number 1234, then setting an initialization parameter
        of 1234 in the SoftLayer_Hardware_Server Service instructs the API to
        act on server record 1234 in your method calls.

        See U{http://sldn.softlayer.com/article/Using-Initialization-Parameters-SoftLayer-API}
        for more information.

        :param id: The id number of the SoftLayer API object to instantiate
        """

        self.add_header(self._service_name + 'InitParameters', {
            'id': int(id)
        })

    def set_object_mask(self, mask):
        """ Set an object mask to a SoftLayer API call [deprecated]

        Use an object mask to retrieve data related your API call's result.
        Object masks are skeleton objects, or strings that define nested
        relational properties to retrieve along with an object's local
        properties. See
        U{http://sldn.softlayer.com/article/Using-Object-Masks-SoftLayer-API}
        for more information.

        :param mask: The object mask you wish to define
        """

        header = 'SoftLayer_ObjectMask'

        if isinstance(mask, dict):
            header = '%sObjectMask' % self._service_name

        self.add_header(header, {'mask': mask})

    def set_result_limit(self, limit, offset=0):
        """ Set a result limit on a SoftLayer API call [deprecated]

        Many SoftLayer API methods return a group of results. These methods
        support a way to limit the number of results retrieved from the
        SoftLayer API in a way akin to an SQL LIMIT statement.

        :param limit: The number of results to limit a SoftLayer API call to.
        :param offset: An optional offset to begin a SoftLayer API call's
        returned result at.
        """

        self.add_header('resultLimit', {
            'limit': int(limit),
            'offset': int(offset)
        })

    def __getitem__(self, name):
        """ Get a SoftLayer Service

        :param name: The name of the service. E.G. SoftLayer_Account
        """
        if not name.startswith(self._prefix):
            name = self._prefix + name
        return Service(self, name)

    def __call__(self, service, method, *args, **kwargs):
        """ Place a SoftLayer API call """
        objectid = kwargs.get('id')
        objectmask = kwargs.get('mask')
        objectfilter = kwargs.get('filter')
        headers = kwargs.get('headers')
        limit = kwargs.get('limit')
        offset = kwargs.get('offset', 0)

        if headers is None:
            headers = {
                'authenticate': {
                    'username': self.username,
                    'apiKey': self.api_key,
                }}

        if objectid is not None:
            headers[service + 'InitParameters'] = {'id': int(objectid)}

        if objectmask is not None:
            mheader = self._prefix + 'ObjectMask'
            if isinstance(objectmask, dict):
                mheader = '%sObjectMask' % service
            headers[mheader] = {'mask': objectmask}

        if objectfilter is not None:
            _objectfilter = {}
            for name, value in objectfilter.items():
                parts = name.split('.')
                _type = parts.pop(0)
                _filter = {}
                _working = _filter
                for i, part in enumerate(parts):
                    if part not in _working:
                        if i == len(parts) - 1:
                            _working[part] = {'operation': value}
                        else:
                            _working[part] = {}
                    _working = _working[part]
                _objectfilter[_type] = _filter
            headers['%sObjectFilter' % service] = _objectfilter

        if limit:
            headers['resultLimit'] = {
                    'limit': int(limit),
                    'offset': int(offset)
                }
        _old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(self._timeout)
        try:
            uri = '/'.join([self._endpoint_url, service])
            self.transport.__extra_headers = self._raw_headers
            proxy = xmlrpclib.ServerProxy(uri, transport=self.transport,
                                          verbose=self.verbose)
            return proxy.__getattr__(method)({'headers': headers}, *args)
        except xmlrpclib.Fault, e:
            raise SoftLayerError(e.faultString)
        finally:
            self._raw_headers = {}
            socket.setdefaulttimeout(_old_timeout)

    def __getattr__(self, name):
        """ Attempt a SoftLayer API call

        Use this as a catch-all so users can call SoftLayer API methods
        directly against their client object. If the property or method
        relating to their client object doesn't exist then assume the user is
        attempting a SoftLayer API call and return a simple function that makes
        an XML-RPC call.
        """
        try:
            return object.__getattr__(self, name)
        except AttributeError:
            def call_handler(*args, **kwargs):
                return self(self._service_name, name, *args,
                    headers=self._headers, **kwargs)
            return call_handler

    def __repr__(self):
        return "<Client: endpoint=%s, user=%s>" \
            % (self._endpoint_url, self.username)


class Service:
    def __init__(self, client, name):
        self.client = client
        self.name = name

    def __call__(self, name, *args, **kwargs):
        return self.client(self.name, name, *args, **kwargs)

    def __getattr__(self, name):
        try:
            return object.__getattr__(self, name)
        except AttributeError:
            def call_handler(*args, **kwargs):
                return self(name, *args, **kwargs)
            return call_handler

    def __repr__(self):
        return "<Service: %s>" % (self.name,)


class ProxyTransport(xmlrpclib.Transport):
    __extra_headers = {}

    def send_content(self, connection, request_body):
        for k, v in self.__extra_headers:
            connection.putheader(k, v)

        connection.putheader("Content-Type", "text/xml")
        connection.putheader("Content-Length", str(len(request_body)))
        connection.endheaders()
        if request_body:
            connection.send(request_body)

class SecureProxyTransport(xmlrpclib.SafeTransport, ProxyTransport):
    pass

