"""
    SoftLayer.API
    ~~~~~~~~~~~~~
    SoftLayer API bindings

    :license: MIT, see LICENSE for more details.
"""
import warnings

from SoftLayer import auth as slauth
from SoftLayer import config
from SoftLayer import consts
from SoftLayer import transports

# pylint: disable=invalid-name


API_PUBLIC_ENDPOINT = consts.API_PUBLIC_ENDPOINT
API_PRIVATE_ENDPOINT = consts.API_PRIVATE_ENDPOINT
__all__ = [
    'create_client_from_env',
    'Client',
    'BaseClient',
    'API_PUBLIC_ENDPOINT',
    'API_PRIVATE_ENDPOINT',
]

VALID_CALL_ARGS = set((
    'id',
    'mask',
    'filter',
    'headers',
    'compress',
    'raw_headers',
    'limit',
    'offset',
))


def create_client_from_env(username=None,
                           api_key=None,
                           endpoint_url=None,
                           timeout=None,
                           auth=None,
                           config_file=None,
                           proxy=None,
                           user_agent=None,
                           transport=None):
    """Creates a SoftLayer API client using your environment.

    Settings are loaded via keyword arguments, environemtal variables and
    config file.

    :param username: an optional API username if you wish to bypass the
        package's built-in username
    :param api_key: an optional API key if you wish to bypass the package's
        built in API key
    :param endpoint_url: the API endpoint base URL you wish to connect to.
        Set this to API_PRIVATE_ENDPOINT to connect via SoftLayer's private
        network.
    :param proxy: proxy to be used to make API calls
    :param integer timeout: timeout for API requests
    :param auth: an object which responds to get_headers() to be inserted into
        the xml-rpc headers. Example: `BasicAuthentication`
    :param config_file: A path to a configuration file used to load settings
    :param user_agent: an optional User Agent to report when making API
        calls if you wish to bypass the packages built in User Agent string
    :param transport: An object that's callable with this signature:
                      transport(SoftLayer.transports.Request)

    Usage:

        >>> import SoftLayer
        >>> client = SoftLayer.create_client_from_env()
        >>> resp = client.call('Account', 'getObject')
        >>> resp['companyName']
        'Your Company'

    """
    settings = config.get_client_settings(username=username,
                                          api_key=api_key,
                                          endpoint_url=endpoint_url,
                                          timeout=timeout,
                                          proxy=proxy,
                                          config_file=config_file)

    # Default the transport to use XMLRPC
    if transport is None:
        transport = transports.XmlRpcTransport(
            endpoint_url=settings.get('endpoint_url'),
            proxy=settings.get('proxy'),
            timeout=settings.get('timeout'),
            user_agent=user_agent,
        )

    # If we have enough information to make an auth driver, let's do it
    if auth is None and settings.get('username') and settings.get('api_key'):
        # NOTE(kmcdonald): some transports mask other transports, so this is
        # a way to find the 'real' one
        real_transport = getattr(transport, 'transport', transport)

        if isinstance(real_transport, transports.XmlRpcTransport):
            auth = slauth.BasicAuthentication(
                settings.get('username'),
                settings.get('api_key'),
            )

        elif isinstance(real_transport, transports.RestTransport):
            auth = slauth.BasicHTTPAuthentication(
                settings.get('username'),
                settings.get('api_key'),
            )

    return BaseClient(auth=auth, transport=transport)


def Client(**kwargs):
    """Get a SoftLayer API Client using environmental settings.

    Deprecated in favor of create_client_from_env()
    """
    warnings.warn("use SoftLayer.create_client_from_env() instead",
                  DeprecationWarning)
    return create_client_from_env(**kwargs)


class BaseClient(object):
    """Base SoftLayer API client.

    :param auth: auth driver that looks like SoftLayer.auth.AuthenticationBase
    :param transport: An object that's callable with this signature:
                      transport(SoftLayer.transports.Request)
    """

    _prefix = "SoftLayer_"

    def __init__(self, auth=None, transport=None):
        self.auth = auth
        self.transport = transport

    def authenticate_with_password(self, username, password,
                                   security_question_id=None,
                                   security_question_answer=None):
        """Performs Username/Password Authentication

        :param string username: your SoftLayer username
        :param string password: your SoftLayer password
        :param int security_question_id: The security question id to answer
        :param string security_question_answer: The answer to the security
                                                question

        """
        self.auth = None
        res = self.call('User_Customer', 'getPortalLoginToken',
                        username,
                        password,
                        security_question_id,
                        security_question_answer)
        self.auth = slauth.TokenAuthentication(res['userId'], res['hash'])
        return res['userId'], res['hash']

    def __getitem__(self, name):
        """Get a SoftLayer Service.

        :param name: The name of the service. E.G. Account

        Usage:
            >>> import SoftLayer
            >>> client = SoftLayer.create_client_from_env()
            >>> client['Account']
            <Service: Account>

        """
        return Service(self, name)

    def call(self, service, method, *args, **kwargs):
        """Make a SoftLayer API call

        :param service: the name of the SoftLayer API service
        :param method: the method to call on the service
        :param \\*args: same optional arguments that ``Service.call`` takes
        :param \\*\\*kwargs: same optional keyword arguments that
                           ``Service.call`` takes

        :param service: the name of the SoftLayer API service

        Usage:
            >>> import SoftLayer
            >>> client = SoftLayer.create_client_from_env()
            >>> client.call('Account', 'getVirtualGuests', mask="id", limit=10)
            [...]

        """
        if kwargs.pop('iter', False):
            return self.iter_call(service, method, *args, **kwargs)

        invalid_kwargs = set(kwargs.keys()) - VALID_CALL_ARGS
        if invalid_kwargs:
            raise TypeError(
                'Invalid keyword arguments: %s' % ','.join(invalid_kwargs))

        if self._prefix and not service.startswith(self._prefix):
            service = self._prefix + service

        http_headers = {'Accept': '*/*'}

        if kwargs.get('compress', True):
            http_headers['Accept-Encoding'] = 'gzip, deflate, compress'
        else:
            http_headers['Accept-Encoding'] = None

        if kwargs.get('raw_headers'):
            http_headers.update(kwargs.get('raw_headers'))

        request = transports.Request()
        request.service = service
        request.method = method
        request.args = args
        request.transport_headers = http_headers
        request.identifier = kwargs.get('id')
        request.mask = kwargs.get('mask')
        request.filter = kwargs.get('filter')
        request.limit = kwargs.get('limit')
        request.offset = kwargs.get('offset')

        if self.auth:
            extra_headers = self.auth.get_headers()
            if extra_headers:
                warnings.warn("auth.get_headers() is deprecated and will be "
                              "removed in the next major version",
                              DeprecationWarning)
                request.headers.update(extra_headers)

            request = self.auth.get_request(request)

        request.headers.update(kwargs.get('headers', {}))
        return self.transport(request)

    __call__ = call

    def iter_call(self, service, method, *args, **kwargs):
        """A generator that deals with paginating through results.

        :param service: the name of the SoftLayer API service
        :param method: the method to call on the service
        :param integer chunk: result size for each API call (defaults to 100)
        :param \\*args: same optional arguments that ``Service.call`` takes
        :param \\*\\*kwargs: same optional keyword arguments that
                           ``Service.call`` takes

        """
        chunk = kwargs.pop('chunk', 100)
        limit = kwargs.pop('limit', None)
        offset = kwargs.pop('offset', 0)

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

    def __repr__(self):
        return "Client(transport=%r, auth=%r)" % (self.transport, self.auth)

    __str__ = __repr__

    def __len__(self):
        return 0


class Service(object):
    """A SoftLayer Service.

        :param client: A SoftLayer.API.Client instance
        :param name str: The service name

    """
    def __init__(self, client, name):
        self.client = client
        self.name = name

    def call(self, name, *args, **kwargs):
        """Make a SoftLayer API call.

        :param method: the method to call on the service
        :param \\*args: (optional) arguments for the remote call
        :param id: (optional) id for the resource
        :param mask: (optional) object mask
        :param dict filter: (optional) filter dict
        :param dict headers: (optional) optional XML-RPC headers
        :param boolean compress: (optional) Enable/Disable HTTP compression
        :param dict raw_headers: (optional) HTTP transport headers
        :param int limit: (optional) return at most this many results
        :param int offset: (optional) offset results by this many
        :param boolean iter: (optional) if True, returns a generator with the
                             results
        :param bool verify: verify SSL cert
        :param cert: client certificate path

        Usage:
            >>> import SoftLayer
            >>> client = SoftLayer.create_client_from_env()
            >>> client['Account'].getVirtualGuests(mask="id", limit=10)
            [...]

        """
        return self.client.call(self.name, name, *args, **kwargs)

    __call__ = call

    def iter_call(self, name, *args, **kwargs):
        """A generator that deals with paginating through results.

        :param method: the method to call on the service
        :param integer chunk: result size for each API call
        :param \\*args: same optional arguments that ``Service.call`` takes
        :param \\*\\*kwargs: same optional keyword arguments that
                           ``Service.call`` takes

        Usage:
            >>> import SoftLayer
            >>> client = SoftLayer.create_client_from_env()
            >>> gen = client.call('Account', 'getVirtualGuests', iter=True)
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
            " Handler that actually makes the API call "
            return self(name, *args, **kwargs)
        return call_handler

    def __repr__(self):
        return "<Service: %s>" % (self.name,)

    __str__ = __repr__
