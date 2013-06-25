"""
    SoftLayer.API
    ~~~~~~~~~~~~~
    SoftLayer API bindings

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from SoftLayer.consts import API_PUBLIC_ENDPOINT, API_PRIVATE_ENDPOINT, \
    USER_AGENT
from SoftLayer.transport import make_xml_rpc_api_call
from SoftLayer.exceptions import SoftLayerError
import os

API_USERNAME = None
API_KEY = None
API_BASE_URL = API_PUBLIC_ENDPOINT
VALID_CALL_ARGS = set([
    'id',
    'mask',
    'filter',
    'headers',
    'raw_headers',
    'limit',
    'offset',
])


class AuthenticationBase(object):
    def get_headers(self):
        raise NotImplementedError


class BasicAuthentication(AuthenticationBase):
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def get_headers(self):
        return {
            'authenticate': {
                'username': self.username,
                'apiKey': self.api_key,
            }
        }

    def __repr__(self):
        return "<BasicAuthentication: %s>" % (self.username)


class Client(object):
    """ A SoftLayer API client.

    :param service_name: the name of the SoftLayer API service to query
    :param integer id: an optional object ID if you're instantiating a
        particular SoftLayer_API object. Setting an ID defines this client's
        initialization parameter.
    :param username: an optional API username if you wish to bypass the
        package's built-in username
    :param api_key: an optional API key if you wish to bypass the package's
        built in API key
    :param endpoint_url: the API endpoint base URL you wish to connect to.
        Set this to API_PRIVATE_ENDPOINT to connect via SoftLayer's private
        network.
    :param integer timeout: timeout for API requests
    :param boolean verbose: prints details about every HTTP request if true
    :param auth: an object which responds to get_headers() to be inserted into
        the xml-rpc headers. Example: `BasicAuthentication`

    Usage:

        >>> import SoftLayer
        >>> client = SoftLayer.Client(username="username", api_key="api_key")
        >>> resp = client['Account'].getObject()
        >>> resp['companyName']
        'Your Company'

    """
    _prefix = "SoftLayer_"

    def __init__(self, service_name=None, id=None, username=None, api_key=None,
                 endpoint_url=None, timeout=None, verbose=False, auth=None):
        self._service_name = service_name
        self.verbose = verbose
        self._headers = {}
        self._raw_headers = {}

        self.auth = auth
        if self.auth is None:
            username = username or API_USERNAME or \
                os.environ.get('SL_USERNAME') or ''
            api_key = api_key or API_KEY or os.environ.get('SL_API_KEY') or ''
            self.auth = BasicAuthentication(username, api_key)
            self.set_authentication(username, api_key)

        if id is not None:
            self.set_init_parameter(int(id))

        self._endpoint_url = (endpoint_url or API_BASE_URL or
                              API_PUBLIC_ENDPOINT).rstrip('/')
        self.timeout = timeout

    def add_raw_header(self, name, value):
        """ Set HTTP headers for API calls.

        :param name: the header name
        :param value: the header value

        ..  deprecated:: 2.0.0

        """
        self._raw_headers[name] = value

    def add_header(self, name, value):
        """ Set a SoftLayer API call header.

        :param name: the header name
        :param value: the header value

        ..  deprecated:: 2.0.0

        """
        name = name.strip()
        if name is None or name == '':
            raise SoftLayerError('Please specify a header name.')

        self._headers[name] = value

    def remove_header(self, name):
        """ Remove a SoftLayer API call header.

        :param name: the header name

        ..  deprecated:: 2.0.0

        """
        if name in self._headers:
            del self._headers[name.strip()]

    def set_authentication(self, username, api_key):
        """ Set user and key to authenticate a SoftLayer API call.

        Use this method if you wish to bypass the API_USER and API_KEY class
        constants and set custom authentication per API call.

        See https://manage.softlayer.com/Administrative/apiKeychain for more
        information.

        :param username: the username to authenticate with
        :param api_key: the user's API key

        ..  deprecated:: 2.0.0

        """
        self.add_header('authenticate', {
            'username': username.strip(),
            'apiKey': api_key.strip(),
        })

    def set_init_parameter(self, id):
        """ Set an initialization parameter header.

        Initialization parameters instantiate a SoftLayer API service object to
        act upon during your API method call. For instance, if your account has
        a server with ID number 1234, then setting an initialization parameter
        of 1234 in the SoftLayer_Hardware_Server Service instructs the API to
        act on server record 1234 in your method calls.

        See http://sldn.softlayer.com/article/Using-Initialization-Parameters-SoftLayer-API  # NOQA
        for more information.

        :param id: the ID of the SoftLayer API object to instantiate

        ..  deprecated:: 2.0.0

        """
        self.add_header(self._service_name + 'InitParameters', {
            'id': int(id)
        })

    def set_object_mask(self, mask):
        """ Set an object mask to a SoftLayer API call.

        Use an object mask to retrieve data related your API call's result.
        Object masks are skeleton objects, or strings that define nested
        relational properties to retrieve along with an object's local
        properties. See
        http://sldn.softlayer.com/article/Using-Object-Masks-SoftLayer-API
        for more information.

        :param mask: the object mask you wish to define

        ..  deprecated:: 2.0.0

        """
        header = 'SoftLayer_ObjectMask'

        if isinstance(mask, dict):
            header = '%sObjectMask' % self._service_name

        self.add_header(header, {'mask': mask})

    def set_result_limit(self, limit, offset=0):
        """ Set a result limit on a SoftLayer API call.

        Many SoftLayer API methods return a group of results. These methods
        support a way to limit the number of results retrieved from the
        SoftLayer API in a way akin to an SQL LIMIT statement.

        :param limit: the number of results to limit a SoftLayer API call to
        :param offset: An optional offset at which to begin a SoftLayer API
                       call's returned result

        ..  deprecated:: 2.0.0

        """
        self.add_header('resultLimit', {
            'limit': int(limit),
            'offset': int(offset)
        })

    def __getitem__(self, name):
        """ Get a SoftLayer Service.

        :param name: The name of the service. E.G. Account

        Usage:
            >>> client['Account']
            <Service: Account>

        """
        return Service(self, name)

    def call(self, service, method, *args, **kwargs):
        """ Make a SoftLayer API call

        :param service: the name of the SoftLayer API service
        :param method: the method to call on the service
        :param \*args: same optional arguments that ``Service.call`` takes
        :param \*\*kwargs: same optional keyword arguments that
                           ``Service.call`` takes

        :param service: the name of the SoftLayer API service

        Usage:
            >>> client['Account'].getVirtualGuests(mask="id", limit=10)
            [...]

        """
        if kwargs.pop('iter', False):
            return self.iter_call(service, method, *args, **kwargs)

        invalid_kwargs = set(kwargs.keys()) - VALID_CALL_ARGS
        if invalid_kwargs:
            raise TypeError(
                'Invalid keyword arguments: %s' % ','.join(invalid_kwargs))

        if not service.startswith(self._prefix):
            service = self._prefix + service

        objectid = kwargs.get('id')
        objectmask = kwargs.get('mask')
        objectfilter = kwargs.get('filter')
        headers = kwargs.get('headers')
        raw_headers = kwargs.get('raw_headers')
        limit = kwargs.get('limit')
        offset = kwargs.get('offset', 0)

        if headers is None:
            headers = self.auth.get_headers()

        http_headers = {
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/xml',
        }
        if self._raw_headers:
            for name, value in self._raw_headers.items():
                http_headers[name] = value
        if raw_headers:
            for name, value in raw_headers.items():
                http_headers[name] = value

        if objectid is not None:
            headers[service + 'InitParameters'] = {'id': int(objectid)}

        if objectmask is not None:
            headers.update(self.__format_object_mask(objectmask, service))

        if objectfilter is not None:
            headers['%sObjectFilter' % service] = objectfilter

        if limit:
            headers['resultLimit'] = {
                'limit': int(limit),
                'offset': int(offset)
            }
        uri = '/'.join([self._endpoint_url, service])
        return make_xml_rpc_api_call(uri, method, args,
                                     headers=headers,
                                     http_headers=http_headers,
                                     timeout=self.timeout,
                                     verbose=self.verbose)

    __call__ = call

    def iter_call(self, service, method,
                  chunk=100, limit=None, offset=0, *args, **kwargs):
        """ A generator that deals with paginating through results.

        :param service: the name of the SoftLayer API service
        :param method: the method to call on the service
        :param integer chunk: result size for each API call
        :param \*args: same optional arguments that ``Service.call`` takes
        :param \*\*kwargs: same optional keyword arguments that
                           ``Service.call`` takes

        """
        if chunk <= 0:
            raise AttributeError("Chunk size should be greater than zero.")

        if limit:
            chunk = min(chunk, limit)

        result_count = 0
        kwargs['iter'] = False
        while True:
            if limit:
                # We've reached the end of the results
                if result_count >= limit:
                    break

                # Don't over-fetch past the given limit
                if chunk + result_count > limit:
                    chunk = limit - result_count
            results = self.call(service, method,
                                offset=offset, limit=chunk, *args, **kwargs)

            # It looks like we ran out results
            if not results:
                break

            # Apparently this method doesn't return a list.
            # Why are you even iterating over this?
            if not isinstance(results, list):
                yield results
                break

            for item in results:
                yield item
                result_count += 1

            offset += chunk

            if len(results) < chunk:
                break

    def __format_object_mask(self, objectmask, service):
        """ Format new and old style object masks into proper headers.

        :param objectmask: a string- or dict-based object mask
        :param service: a SoftLayer API service name

        """
        if isinstance(objectmask, dict):
            mheader = '%sObjectMask' % service
        else:
            mheader = self._prefix + 'ObjectMask'

            objectmask = objectmask.strip()
            if objectmask.startswith('mask'):
                objectmask = objectmask[4:]
                if objectmask[0] == '.':
                    objectmask = objectmask[1:]
                elif objectmask[0] == '[' and objectmask[-1] == ']':
                    objectmask = objectmask[1:-1]
                else:
                    raise SoftLayerError('Malformed Mask: %s' % objectmask)
            objectmask = "mask[%s]" % objectmask

        return {mheader: {'mask': objectmask}}

    def __getattr__(self, name):
        """ Attempt a SoftLayer API call.

        Use this as a catch-all so users can call SoftLayer API methods
        directly against their client object. If the property or method
        relating to their client object doesn't exist then assume the user is
        attempting a SoftLayer API call and return a simple function that makes
        an XML-RPC call.

        :param name: method name

        ..  deprecated:: 2.0.0

        """
        if name in ["__name__", "__bases__"]:
            raise AttributeError("'Obj' object has no attribute '%s'" % name)

        def call_handler(*args, **kwargs):
            if self._service_name is None:
                raise SoftLayerError(
                    "Service is not set on Client instance.")
            kwargs['headers'] = self._headers
            return self.call(self._service_name, name, *args, **kwargs)
        return call_handler

    def __repr__(self):
        return "<Client: endpoint=%s, user=%r>" \
            % (self._endpoint_url, self.auth)

    __str__ = __repr__


class Service(object):
    def __init__(self, client, name):
        self.client = client
        self.name = name

    def call(self, name, *args, **kwargs):
        """ Make a SoftLayer API call

        :param method: the method to call on the service
        :param \*args: (optional) arguments for the remote call
        :param id: (optional) id for the resource
        :param mask: (optional) object mask
        :param dict filter: (optional) filter dict
        :param dict headers: (optional) optional XML-RPC headers
        :param dict raw_headers: (optional) HTTP transport headers
        :param int limit: (optional) return at most this many results
        :param int offset: (optional) offset results by this many
        :param boolean iter: (optional) if True, returns a generator with the
                             results

        Usage:
            >>> client['Account'].getVirtualGuests(mask="id", limit=10)
            [...]

        """
        return self.client.call(self.name, name, *args, **kwargs)

    __call__ = call

    def iter_call(self, name, *args, **kwargs):
        """ A generator that deals with paginating through results.

        :param method: the method to call on the service
        :param integer chunk: result size for each API call
        :param \*args: same optional arguments that ``Service.call`` takes
        :param \*\*kwargs: same optional keyword arguments that
                           ``Service.call`` takes

        Usage:
            >>> gen = client['Account'].getVirtualGuests(iter=True)
            >>> for virtual_guest in gen:
            ...     virtual_guest['id']
            ...
            1234
            4321

        """
        return self.client.iter_call(self.name, name, *args, **kwargs)

    def __getattr__(self, name):
        if name in ["__name__", "__bases__"]:
            raise AttributeError("'Obj' object has no attribute '%s'" % name)

        def call_handler(*args, **kwargs):
            return self(name, *args, **kwargs)
        return call_handler

    def __repr__(self):
        return "<Service: %s>" % (self.name,)

    __str__ = __repr__
