"""
    SoftLayer.API
    ~~~~~~~~~~~~~
    SoftLayer API bindings

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=invalid-name
import time

import concurrent.futures as cf
import json
import logging
import math
import requests

from SoftLayer import auth as slauth
from SoftLayer import config
from SoftLayer import consts
from SoftLayer import exceptions
from SoftLayer import transports
from SoftLayer import utils

LOGGER = logging.getLogger(__name__)
API_PUBLIC_ENDPOINT = consts.API_PUBLIC_ENDPOINT
API_PRIVATE_ENDPOINT = consts.API_PRIVATE_ENDPOINT
CONFIG_FILE = consts.CONFIG_FILE

__all__ = [
    'create_client_from_env',
    'employee_client',
    'Client',
    'BaseClient',
    'API_PUBLIC_ENDPOINT',
    'API_PRIVATE_ENDPOINT',
    'IAMClient',
    'CertificateClient'
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
    'verify'
))


def create_client_from_env(username=None,
                           api_key=None,
                           endpoint_url=None,
                           timeout=None,
                           auth=None,
                           config_file=None,
                           proxy=None,
                           user_agent=None,
                           transport=None,
                           verify=True):
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
    :param bool verify: decide to verify the server's SSL/TLS cert. DO NOT SET
                        TO FALSE WITHOUT UNDERSTANDING THE IMPLICATIONS.

    Usage:

        >>> import SoftLayer
        >>> client = SoftLayer.create_client_from_env()
        >>> resp = client.call('Account', 'getObject')
        >>> resp['companyName']
        'Your Company'

    """
    if config_file is None:
        config_file = CONFIG_FILE
    settings = config.get_client_settings(username=username,
                                          api_key=api_key,
                                          endpoint_url=endpoint_url,
                                          timeout=timeout,
                                          proxy=proxy,
                                          verify=verify,
                                          config_file=config_file)

    if transport is None:
        url = settings.get('endpoint_url')
        if url is not None and '/rest' in url:
            # If this looks like a rest endpoint, use the rest transport
            transport = transports.RestTransport(
                endpoint_url=settings.get('endpoint_url'),
                proxy=settings.get('proxy'),
                timeout=settings.get('timeout'),
                user_agent=user_agent,
                verify=verify,
            )
        else:
            # Default the transport to use XMLRPC
            transport = transports.XmlRpcTransport(
                endpoint_url=settings.get('endpoint_url'),
                proxy=settings.get('proxy'),
                timeout=settings.get('timeout'),
                user_agent=user_agent,
                verify=verify,
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

    return BaseClient(auth=auth, transport=transport, config_file=config_file)


def employee_client(username=None,
                    access_token=None,
                    endpoint_url=None,
                    timeout=None,
                    auth=None,
                    config_file=None,
                    proxy=None,
                    user_agent=None,
                    transport=None,
                    verify=True):
    """Creates an INTERNAL SoftLayer API client using your environment.

    Settings are loaded via keyword arguments, environemtal variables and config file.

    :param username: your user ID
    :param access_token: hash from SoftLayer_User_Employee::performExternalAuthentication(username, password, token)
    :param password: password to use for employee authentication
    :param endpoint_url: the API endpoint base URL you wish to connect to.
        Set this to API_PRIVATE_ENDPOINT to connect via SoftLayer's private network.
    :param proxy: proxy to be used to make API calls
    :param integer timeout: timeout for API requests
    :param auth: an object which responds to get_headers() to be inserted into the xml-rpc headers.
        Example: `BasicAuthentication`
    :param config_file: A path to a configuration file used to load settings
    :param user_agent: an optional User Agent to report when making API
        calls if you wish to bypass the packages built in User Agent string
    :param transport: An object that's callable with this signature: transport(SoftLayer.transports.Request)
    :param bool verify: decide to verify the server's SSL/TLS cert.
    """
    settings = config.get_client_settings(username=username,
                                          api_key=None,
                                          endpoint_url=endpoint_url,
                                          timeout=timeout,
                                          proxy=proxy,
                                          verify=None,
                                          config_file=config_file)

    url = settings.get('endpoint_url', '')
    verify = settings.get('verify', True)

    if 'internal' not in url:
        raise exceptions.SoftLayerError(f"{url} does not look like an Internal Employee url.")

    if transport is None:
        if url is not None and '/rest' in url:
            # If this looks like a rest endpoint, use the rest transport
            transport = transports.RestTransport(
                endpoint_url=url,
                proxy=settings.get('proxy'),
                timeout=settings.get('timeout'),
                user_agent=user_agent,
                verify=verify,
            )
        else:
            # Default the transport to use XMLRPC
            transport = transports.XmlRpcTransport(
                endpoint_url=url,
                proxy=settings.get('proxy'),
                timeout=settings.get('timeout'),
                user_agent=user_agent,
                verify=verify,
            )

    if access_token is None:
        access_token = settings.get('access_token')

    user_id = settings.get('userid')
    # Assume access_token is valid for now, user has logged in before at least.
    if settings.get('auth_cert', False):
        auth = slauth.X509Authentication(settings.get('auth_cert'), verify)
        return EmployeeClient(auth=auth, transport=transport, config_file=config_file)
    elif access_token and user_id:
        auth = slauth.EmployeeAuthentication(user_id, access_token)
        return EmployeeClient(auth=auth, transport=transport, config_file=config_file)
    else:
        # This is for logging in mostly.
        LOGGER.info("No access_token or userid found in settings, creating a No Auth client for now.")
        return EmployeeClient(auth=None, transport=transport, config_file=config_file)


def Client(**kwargs):
    """Get a SoftLayer API Client using environmental settings."""
    return create_client_from_env(**kwargs)


class BaseClient(object):
    """Base SoftLayer API client.

    :param auth: auth driver that looks like SoftLayer.auth.AuthenticationBase
    :param transport: An object that's callable with this signature: transport(SoftLayer.transports.Request)
    """
    _prefix = "SoftLayer_"
    auth: slauth.AuthenticationBase

    def __init__(self, auth=None, transport=None, config_file=None):
        if config_file is None:
            config_file = CONFIG_FILE
        self.config_file = config_file
        self.settings = config.get_config(self.config_file)
        self.__setAuth(auth)
        self.__setTransport(transport)

    def __setAuth(self, auth=None):
        """Prepares the authentication property"""
        self.auth = auth

    def __setTransport(self, transport=None):
        """Prepares the transport property"""
        verify = self.settings['softlayer'].get('verify')
        if verify == "False":
            verify = False
        elif verify == "True":
            verify = True
        if transport is None:
            url = self.settings['softlayer'].get('endpoint_url')
            if url is not None and '/rest' in url:
                # If this looks like a rest endpoint, use the rest transport
                transport = transports.RestTransport(
                    endpoint_url=url,
                    proxy=self.settings['softlayer'].get('proxy'),
                    # prevents an exception incase timeout is a float number.
                    timeout=int(self.settings['softlayer'].getfloat('timeout', 0)),
                    user_agent=consts.USER_AGENT,
                    verify=verify,
                )
            else:
                # Default the transport to use XMLRPC
                transport = transports.XmlRpcTransport(
                    endpoint_url=url,
                    proxy=self.settings['softlayer'].get('proxy'),
                    timeout=int(self.settings['softlayer'].getfloat('timeout', 0)),
                    user_agent=consts.USER_AGENT,
                    verify=verify,
                )

        self.transport = transport

    def authenticate_with_password(self, username, password, security_question_id=None, security_question_answer=None):
        """Performs Username/Password Authentication

        :param string username: your SoftLayer username
        :param string password: your SoftLayer password
        :param int security_question_id: The security question id to answer
        :param string security_question_answer: The answer to the security question

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
        :param boolean iter: (optional) if True, returns a generator with the results
        :param bool verify: verify SSL cert
        :param cert: client certificate path

        Usage:
            >>> import SoftLayer
            >>> client = SoftLayer.create_client_from_env()
            >>> client.call('Account', 'getVirtualGuests', mask="id", limit=10)
            [...]

        """
        if kwargs.pop('iter', False):
            # Most of the codebase assumes a non-generator will be returned, so casting to list
            # keeps those sections working
            return list(self.iter_call(service, method, *args, **kwargs))

        invalid_kwargs = set(kwargs.keys()) - VALID_CALL_ARGS
        if invalid_kwargs:
            raise TypeError('Invalid keyword arguments: %s' % ','.join(invalid_kwargs))

        prefixes = (self._prefix, 'BluePages_Search', 'IntegratedOfferingTeam_Region')
        if self._prefix and not service.startswith(prefixes):
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
        request.url = self.settings['softlayer'].get('endpoint_url')
        if kwargs.get('verify') is not None:
            request.verify = kwargs.get('verify')
        if self.auth:
            request = self.auth.get_request(request)

        request.headers.update(kwargs.get('headers', {}))
        return self.transport(request)

    __call__ = call

    def iter_call(self, service, method, *args, **kwargs):
        """A generator that deals with paginating through results.

        :param service: the name of the SoftLayer API service
        :param method: the method to call on the service
        :param integer limit: result size for each API call (defaults to 100)
        :param \\*args: same optional arguments that ``Service.call`` takes
        :param \\*\\*kwargs: same optional keyword arguments that ``Service.call`` takes

        """

        limit = kwargs.pop('limit', 100)
        offset = kwargs.pop('offset', 0)

        if limit <= 0:
            raise AttributeError("Limit size should be greater than zero.")

        # Set to make unit tests, which call this function directly, play nice.
        kwargs['iter'] = False
        result_count = 0
        keep_looping = True
        kwargs['filter'] = utils.fix_filter(kwargs.get('filter'))

        while keep_looping:
            # Get the next results
            results = self.call(service, method, offset=offset, limit=limit, *args, **kwargs)

            # Apparently this method doesn't return a list.
            # Why are you even iterating over this?
            if not isinstance(results, transports.SoftLayerListResult):
                if isinstance(results, list):
                    # Close enough, this makes testing a lot easier
                    results = transports.SoftLayerListResult(results, len(results))
                else:
                    yield results
                    return

            for item in results:
                yield item
                result_count += 1

            # Got less results than requested, we are at the end
            if len(results) < limit:
                keep_looping = False
            # Got all the needed items
            if result_count >= results.total_count:
                keep_looping = False

            offset += limit

    def cf_call(self, service, method, *args, **kwargs):
        """Uses threads to iterate through API calls.

        :param service: the name of the SoftLayer API service
        :param method: the method to call on the service
        :param integer limit: result size for each API call (defaults to 100)
        :param \\*args: same optional arguments that ``Service.call`` takes
        :param \\*\\*kwargs: same optional keyword arguments that ``Service.call`` takes
        """
        limit = kwargs.pop('limit', 100)
        offset = kwargs.pop('offset', 0)

        if limit <= 0:
            raise AttributeError("Limit size should be greater than zero.")
        # This initial API call is to determine how many API calls we need to make after this first one.
        first_call = self.call(service, method, offset=offset, limit=limit, *args, **kwargs)

        # This was not a list result, just return it.
        if not isinstance(first_call, transports.SoftLayerListResult):
            return first_call
        # How many more API calls we have to make
        api_calls = math.ceil((first_call.total_count - limit) / limit)

        def this_api(offset):
            """Used to easily call executor.map() on this fuction"""
            return self.call(service, method, offset=offset, limit=limit, *args, **kwargs)

        with cf.ThreadPoolExecutor(max_workers=10) as executor:
            future_results = {}
            offset_map = [x * limit for x in range(1, api_calls)]
            future_results = list(executor.map(this_api, offset_map))
        # Append the results in the order they were called
        for call_result in future_results:
            first_call = first_call + call_result
        return first_call

    def __repr__(self):
        return "Client(transport=%r, auth=%r)" % (self.transport, self.auth)

    __str__ = __repr__

    def __len__(self):
        return 0


class CertificateClient(BaseClient):
    """Client that works with a X509 Certificate for authentication.

    Will read the certificate file from the config file (~/.softlayer usually).
    > auth_cert = /path/to/authentication/cert.pm
    > server_cert = /path/to/CAcert.pem
    Set auth to a SoftLayer.auth.Authentication class to manually set authentication
    """

    def __init__(self, auth=None, transport=None, config_file=None):
        BaseClient.__init__(self, auth, transport, config_file)
        self.__setAuth(auth)

    def __setAuth(self, auth=None):
        """Prepares the authentication property"""
        if auth is None:
            auth_cert = self.settings['softlayer'].get('auth_cert')
            serv_cert = self.settings['softlayer'].get('verify', True)
            auth = slauth.X509Authentication(auth_cert, serv_cert)
        self.auth = auth

    def __repr__(self):
        return "CertificateClient(transport=%r, auth=%r)" % (self.transport, self.auth)


class IAMClient(BaseClient):
    """IBM ID Client for using IAM authentication

    :param auth: auth driver that looks like SoftLayer.auth.AuthenticationBase
    :param transport: An object that's callable with this signature: transport(SoftLayer.transports.Request)
    """

    def authenticate_with_password(self, username, password, security_question_id=None, security_question_answer=None):
        """Performs IBM IAM Username/Password Authentication

        :param string username: your IBMid username
        :param string password: your IBMid password
        """

        iam_client = requests.Session()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': consts.USER_AGENT,
            'Accept': 'application/json'
        }
        data = {
            'grant_type': 'password',
            'password': password,
            'response_type': 'cloud_iam',
            'username': username
        }

        try:
            response = iam_client.request(
                'POST',
                'https://iam.cloud.ibm.com/identity/token',
                data=data,
                headers=headers,
                auth=requests.auth.HTTPBasicAuth('bx', 'bx')
            )
            if response.status_code != 200:
                LOGGER.error("Unable to login: %s", response.text)

            response.raise_for_status()
            tokens = json.loads(response.text)
        except requests.HTTPError as ex:
            error = json.loads(response.text)
            raise exceptions.IAMError(response.status_code,
                                      error.get('errorMessage'),
                                      'https://iam.cloud.ibm.com/identity/token') from ex

        self.settings['softlayer']['access_token'] = tokens['access_token']
        self.settings['softlayer']['refresh_token'] = tokens['refresh_token']

        config.write_config(self.settings, self.config_file)
        self.auth = slauth.BearerAuthentication('', tokens['access_token'], tokens['refresh_token'])

        return tokens

    def authenticate_with_passcode(self, passcode):
        """Performs IBM IAM SSO Authentication

        :param string passcode: your IBMid password
        """

        iam_client = requests.Session()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': consts.USER_AGENT,
            'Accept': 'application/json'
        }
        data = {
            'grant_type': 'urn:ibm:params:oauth:grant-type:passcode',
            'passcode': passcode,
            'response_type': 'cloud_iam'
        }

        try:
            response = iam_client.request(
                'POST',
                'https://iam.cloud.ibm.com/identity/token',
                data=data,
                headers=headers,
                auth=requests.auth.HTTPBasicAuth('bx', 'bx')
            )
            if response.status_code != 200:
                LOGGER.error("Unable to login: %s", response.text)

            response.raise_for_status()
            tokens = json.loads(response.text)

        except requests.HTTPError as ex:
            error = json.loads(response.text)
            raise exceptions.IAMError(response.status_code,
                                      error.get('errorMessage'),
                                      'https://iam.cloud.ibm.com/identity/token') from ex

        self.settings['softlayer']['access_token'] = tokens['access_token']
        self.settings['softlayer']['refresh_token'] = tokens['refresh_token']
        a_expire = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tokens['expiration']))
        r_expire = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tokens['refresh_token_expiration']))
        LOGGER.warning("Tokens retrieved, expires at %s, Refresh expires at %s", a_expire, r_expire)
        config.write_config(self.settings, self.config_file)
        self.auth = slauth.BearerAuthentication('', tokens['access_token'], tokens['refresh_token'])

        return tokens

    def authenticate_with_iam_token(self, a_token, r_token=None):
        """Authenticates to the SL API  with an IAM Token

        :param string a_token: Access token
        :param string r_token: Refresh Token, to be used if Access token is expired.
        """
        self.auth = slauth.BearerAuthentication('', a_token, r_token)

    def refresh_iam_token(self, r_token, account_id=None, ims_account=None):
        """Refreshes the IAM Token, will default to values in the config file"""
        iam_client = requests.Session()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': consts.USER_AGENT,
            'Accept': 'application/json'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': r_token,
            'response_type': 'cloud_iam'
        }

        sl_config = self.settings['softlayer']

        if account_id is None and sl_config.get('account_id', False):
            account_id = sl_config.get('account_id')
        if ims_account is None and sl_config.get('ims_account', False):
            ims_account = sl_config.get('ims_account')

        data['account'] = account_id
        data['ims_account'] = ims_account

        try:
            response = iam_client.request(
                'POST',
                'https://iam.cloud.ibm.com/identity/token',
                data=data,
                headers=headers,
                auth=requests.auth.HTTPBasicAuth('bx', 'bx')
            )

            if response.status_code != 200:
                LOGGER.warning("Unable to refresh IAM Token. %s", response.text)

            response.raise_for_status()
            tokens = json.loads(response.text)

        except requests.HTTPError as ex:
            error = json.loads(response.text)
            raise exceptions.IAMError(response.status_code,
                                      error.get('errorMessage'),
                                      'https://iam.cloud.ibm.com/identity/token') from ex

        a_expire = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tokens['expiration']))
        r_expire = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tokens['refresh_token_expiration']))
        LOGGER.warning("Tokens retrieved, expires at %s, Refresh expires at %s", a_expire, r_expire)

        self.settings['softlayer']['access_token'] = tokens['access_token']
        self.settings['softlayer']['refresh_token'] = tokens['refresh_token']
        config.write_config(self.settings, self.config_file)
        self.auth = slauth.BearerAuthentication('', tokens['access_token'])
        return tokens

    def call(self, service, method, *args, **kwargs):
        """Handles refreshing IAM tokens in case of a HTTP 401 error"""
        try:
            return super().call(service, method, *args, **kwargs)
        except exceptions.SoftLayerAPIError as ex:

            if ex.faultCode == 401:
                LOGGER.warning("Token has expired, trying to refresh. %s", ex.faultString)
                return ex
            else:
                raise ex

    def __repr__(self):
        return "IAMClient(transport=%r, auth=%r)" % (self.transport, self.auth)


class EmployeeClient(BaseClient):
    """Internal SoftLayer Client

    :param auth: auth driver that looks like SoftLayer.auth.AuthenticationBase
    :param transport: An object that's callable with this signature: transport(SoftLayer.transports.Request)
    """

    def __init__(self, auth=None, transport=None, config_file=None, account_id=None):
        BaseClient.__init__(self, auth, transport, config_file)
        self.account_id = account_id

    def authenticate_with_internal(self, username, password, security_token=None):
        """Performs internal authentication

        :param string username: your softlayer username
        :param string password: your softlayer password
        :param int security_token: your 2FA token, prompt if None
        """

        self.auth = None
        if security_token is None:
            security_token = input("Enter your 2FA Token now: ")
            if len(security_token) != 6:
                raise exceptions.SoftLayerAPIError("Invalid security token: {}".format(security_token))

        auth_result = self.call('SoftLayer_User_Employee', 'getEncryptedSessionToken',
                                username, password, security_token)

        self.settings['softlayer']['access_token'] = auth_result['hash']
        self.settings['softlayer']['userid'] = str(auth_result['userId'])
        # self.settings['softlayer']['refresh_token'] = tokens['refresh_token']

        config.write_config(self.settings, self.config_file)
        self.auth = slauth.EmployeeAuthentication(auth_result['userId'], auth_result['hash'])

        return auth_result

    def authenticate_with_hash(self, userId, access_token):
        """Authenticates to the Internal SL API with an employee userid + token

        :param string userId: Employee UserId
        :param string access_token: Employee Hash Token
        """
        self.auth = slauth.EmployeeAuthentication(userId, access_token)

    def refresh_token(self, userId, auth_token):
        """Refreshes the login token"""

        # Go directly to base client, to avoid infite loop if the token is super expired.
        auth_result = BaseClient.call(self, 'SoftLayer_User_Employee', 'refreshEncryptedToken', auth_token, id=userId)
        if len(auth_result) > 1:
            for returned_data in auth_result:
                # Access tokens should be 188 characters, but just incase its longer or something.
                if len(returned_data) > 180:
                    self.settings['softlayer']['access_token'] = returned_data
        else:
            message = "Excepted 2 properties from refreshEncryptedToken, got {}|".format(auth_result)
            raise exceptions.SoftLayerAPIError(message)

        config.write_config(self.settings, self.config_file)
        self.auth = slauth.EmployeeAuthentication(userId, auth_result[0])
        return auth_result

    def call(self, service, method, *args, **kwargs):
        """Handles refreshing Employee tokens in case of a HTTP 401 error"""
        if (service == 'SoftLayer_Account' or service == 'Account') and not kwargs.get('id'):
            if not self.account_id:
                raise exceptions.SoftLayerError("SoftLayer_Account service requires an ID")
            kwargs['id'] = self.account_id

        try:
            return BaseClient.call(self, service, method, *args, **kwargs)
        except exceptions.SoftLayerAPIError as ex:
            if ex.faultCode == "SoftLayer_Exception_EncryptedToken_Expired":
                userId = self.settings['softlayer'].get('userid')
                access_token = self.settings['softlayer'].get('access_token')
                LOGGER.warning("Token has expired, trying to refresh. %s", ex.faultString)
                self.refresh_token(userId, access_token)
                # Try the Call again this time....
                return BaseClient.call(self, service, method, *args, **kwargs)

            else:
                raise ex

    def __repr__(self):
        return "EmployeeClient(transport=%r, auth=%r)" % (self.transport, self.auth)


class Service(object):
    """A SoftLayer Service.

        :param client: A SoftLayer.API.Client instance
        :param name str: The service name

    """

    def __init__(self, client, name):
        self.client = client
        self.name = name

    def call(self, name, *args, **kwargs):
        """Make a SoftLayer API call

        :param service: the name of the SoftLayer API service
        :param method: the method to call on the service
        :param \\*args: same optional arguments that ``BaseClient.call`` takes
        :param \\*\\*kwargs: same optional keyword arguments that
                           ``BaseClient.call`` takes

        :param service: the name of the SoftLayer API service

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
