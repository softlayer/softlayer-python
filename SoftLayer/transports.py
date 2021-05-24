"""
    SoftLayer.transports
    ~~~~~~~~~~~~~~~~~~~~
    XML-RPC transport layer that uses the requests library.

    :license: MIT, see LICENSE for more details.
"""
import base64
import importlib
import json
import logging
import re
from string import Template
import time
import xmlrpc.client

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from SoftLayer import consts
from SoftLayer import exceptions
from SoftLayer import utils

LOGGER = logging.getLogger(__name__)
# transports.Request does have a lot of instance attributes. :(
# pylint: disable=too-many-instance-attributes, no-self-use

__all__ = [
    'Request',
    'XmlRpcTransport',
    'RestTransport',
    'TimingTransport',
    'DebugTransport',
    'FixtureTransport',
    'SoftLayerListResult',
]

REST_SPECIAL_METHODS = {
    # 'deleteObject': 'DELETE',
    'createObject': 'POST',
    'createObjects': 'POST',
    'editObject': 'PUT',
    'editObjects': 'PUT',
}


def get_session(user_agent):
    """Sets up urllib sessions"""

    client = requests.Session()
    client.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': user_agent,
    })
    retry = Retry(connect=3, backoff_factor=3)
    adapter = HTTPAdapter(max_retries=retry)
    client.mount('https://', adapter)
    return client


class Request(object):
    """Transport request object."""

    def __init__(self):
        #: API service name. E.G. SoftLayer_Account
        self.service = None

        #: API method name. E.G. getObject
        self.method = None

        #: API Parameters.
        self.args = tuple()

        #: API headers, used for authentication, masks, limits, offsets, etc.
        self.headers = {}

        #: Transport user.
        self.transport_user = None

        #: Transport password.
        self.transport_password = None

        #: Transport headers.
        self.transport_headers = {}

        #: Boolean specifying if the server certificate should be verified.
        self.verify = None

        #: Client certificate file path.
        self.cert = None

        #: InitParameter/identifier of an object.
        self.identifier = None

        #: SoftLayer mask (dict or string).
        self.mask = None

        #: SoftLayer Filter (dict).
        self.filter = None

        #: Integer result limit.
        self.limit = None

        #: Integer result offset.
        self.offset = None

        #: Integer call start time
        self.start_time = None

        #: Integer call end time
        self.end_time = None

        #: String full url
        self.url = None

        #: String result of api call
        self.result = None

        #: String payload to send in
        self.payload = None

        #: Exception any exceptions that got caught
        self.exception = None

    def __repr__(self):
        """Prints out what this call is all about"""
        pretty_mask = utils.clean_string(self.mask)
        pretty_filter = self.filter
        param_string = "id={id}, mask='{mask}', filter='{filter}', args={args}, limit={limit}, offset={offset}".format(
            id=self.identifier, mask=pretty_mask, filter=pretty_filter,
            args=self.args, limit=self.limit, offset=self.offset)
        return "{service}::{method}({params})".format(
            service=self.service, method=self.method, params=param_string)


class SoftLayerListResult(list):
    """A SoftLayer API list result."""

    def __init__(self, items=None, total_count=0):

        #: total count of items that exist on the server. This is useful when
        #: paginating through a large list of objects.
        self.total_count = total_count
        super().__init__(items)


class XmlRpcTransport(object):
    """XML-RPC transport."""

    def __init__(self, endpoint_url=None, timeout=None, proxy=None, user_agent=None, verify=True):

        self.endpoint_url = (endpoint_url or consts.API_PUBLIC_ENDPOINT).rstrip('/')
        self.timeout = timeout or None
        self.proxy = proxy
        self.user_agent = user_agent or consts.USER_AGENT
        self.verify = verify
        self._client = None

    @property
    def client(self):
        """Returns client session object"""

        if self._client is None:
            self._client = get_session(self.user_agent)
        return self._client

    def __call__(self, request):
        """Makes a SoftLayer API call against the XML-RPC endpoint.

        :param request request: Request object
        """
        largs = list(request.args)
        headers = request.headers

        auth = None
        if request.transport_user:
            auth = requests.auth.HTTPBasicAuth(request.transport_user, request.transport_password)

        if request.identifier is not None:
            header_name = request.service + 'InitParameters'
            headers[header_name] = {'id': request.identifier}

        if request.mask is not None:
            if isinstance(request.mask, dict):
                mheader = '%sObjectMask' % request.service
            else:
                mheader = 'SoftLayer_ObjectMask'
                request.mask = _format_object_mask(request.mask)
            headers.update({mheader: {'mask': request.mask}})

        if request.filter is not None:
            headers['%sObjectFilter' % request.service] = request.filter

        if request.limit:
            headers['resultLimit'] = {
                'limit': request.limit,
                'offset': request.offset or 0,
            }

        largs.insert(0, {'headers': headers})
        request.transport_headers.setdefault('Content-Type', 'application/xml')
        request.transport_headers.setdefault('User-Agent', self.user_agent)

        request.url = '/'.join([self.endpoint_url, request.service])
        request.payload = xmlrpc.client.dumps(tuple(largs),
                                              methodname=request.method,
                                              allow_none=True)

        # Prefer the request setting, if it's not None
        verify = request.verify
        if verify is None:
            request.verify = self.verify

        try:
            resp = self.client.request('POST', request.url,
                                       data=request.payload,
                                       auth=auth,
                                       headers=request.transport_headers,
                                       timeout=self.timeout,
                                       verify=request.verify,
                                       cert=request.cert,
                                       proxies=_proxies_dict(self.proxy))

            resp.raise_for_status()
            result = xmlrpc.client.loads(resp.content)[0][0]
            if isinstance(result, list):
                return SoftLayerListResult(
                    result, int(resp.headers.get('softlayer-total-items', 0)))
            else:
                return result
        except xmlrpc.client.Fault as ex:
            # These exceptions are formed from the XML-RPC spec
            # http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php
            error_mapping = {
                '-32700': exceptions.NotWellFormed,
                '-32701': exceptions.UnsupportedEncoding,
                '-32702': exceptions.InvalidCharacter,
                '-32600': exceptions.SpecViolation,
                '-32601': exceptions.MethodNotFound,
                '-32602': exceptions.InvalidMethodParameters,
                '-32603': exceptions.InternalError,
                '-32500': exceptions.ApplicationError,
                '-32400': exceptions.RemoteSystemError,
                '-32300': exceptions.TransportError,
            }
            _ex = error_mapping.get(ex.faultCode, exceptions.SoftLayerAPIError)
            raise _ex(ex.faultCode, ex.faultString) from ex
        except requests.HTTPError as ex:
            raise exceptions.TransportError(ex.response.status_code, str(ex))
        except requests.RequestException as ex:
            raise exceptions.TransportError(0, str(ex))

    def print_reproduceable(self, request):
        """Prints out the minimal python code to reproduce a specific request

        The will also automatically replace the API key so its not accidently exposed.

        :param request request: Request object
        """
        output = Template('''============= testing.py =============
import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from xml.etree import ElementTree
client = requests.Session()
client.headers.update({'Content-Type': 'application/json', 'User-Agent': 'softlayer-python/testing',})
retry = Retry(connect=3, backoff_factor=3)
adapter = HTTPAdapter(max_retries=retry)
client.mount('https://', adapter)
# This is only needed if you are using an cloud.ibm.com api key
#auth=HTTPBasicAuth('apikey', YOUR_CLOUD_API_KEY)
auth=None
url = '$url'
payload = """$payload"""
transport_headers = $transport_headers
timeout = $timeout
verify = $verify
cert = $cert
proxy = $proxy
response = client.request('POST', url, data=payload, headers=transport_headers, timeout=timeout,
               verify=verify, cert=cert, proxies=proxy, auth=auth)
xml = ElementTree.fromstring(response.content)
ElementTree.dump(xml)
==========================''')

        safe_payload = re.sub(r'<string>[a-z0-9]{64}</string>', r'<string>API_KEY_GOES_HERE</string>', request.payload)
        safe_payload = re.sub(r'(\s+)', r' ', safe_payload)
        substitutions = dict(url=request.url, payload=safe_payload, transport_headers=request.transport_headers,
                             timeout=self.timeout, verify=request.verify, cert=request.cert,
                             proxy=_proxies_dict(self.proxy))
        return output.substitute(substitutions)


class RestTransport(object):
    """REST transport.

    REST calls should mostly work, but is not fully tested.
    XML-RPC should be used when in doubt
    """

    def __init__(self, endpoint_url=None, timeout=None, proxy=None, user_agent=None, verify=True):

        self.endpoint_url = (endpoint_url or consts.API_PUBLIC_ENDPOINT_REST).rstrip('/')
        self.timeout = timeout or None
        self.proxy = proxy
        self.user_agent = user_agent or consts.USER_AGENT
        self.verify = verify
        self._client = None

    @property
    def client(self):
        """Returns client session object"""

        if self._client is None:
            self._client = get_session(self.user_agent)
        return self._client

    def __call__(self, request):
        """Makes a SoftLayer API call against the REST endpoint.

        REST calls should mostly work, but is not fully tested.
        XML-RPC should be used when in doubt

        :param request request: Request object
        """
        params = request.headers.copy()
        if request.mask:
            request.mask = _format_object_mask(request.mask)
            params['objectMask'] = request.mask

        if request.limit or request.offset:
            limit = request.limit or 0
            offset = request.offset or 0
            params['resultLimit'] = "%d,%d" % (offset, limit)

        if request.filter:
            params['objectFilter'] = json.dumps(request.filter)

        request.params = params

        auth = None
        if request.transport_user:
            auth = requests.auth.HTTPBasicAuth(
                request.transport_user,
                request.transport_password,
            )

        method = REST_SPECIAL_METHODS.get(request.method)

        if method is None:
            method = 'GET'

        body = {}
        if request.args:
            # NOTE(kmcdonald): force POST when there are arguments because
            # the request body is ignored otherwise.
            method = 'POST'
            body['parameters'] = request.args

        if body:
            request.payload = json.dumps(body, cls=ComplexEncoder)

        url_parts = [self.endpoint_url, request.service]
        if request.identifier is not None:
            url_parts.append(str(request.identifier))

        if request.method is not None:
            url_parts.append(request.method)

        request.url = '%s.%s' % ('/'.join(url_parts), 'json')

        # Prefer the request setting, if it's not None

        if request.verify is None:
            request.verify = self.verify

        try:
            resp = self.client.request(method, request.url,
                                       auth=auth,
                                       headers=request.transport_headers,
                                       params=request.params,
                                       data=request.payload,
                                       timeout=self.timeout,
                                       verify=request.verify,
                                       cert=request.cert,
                                       proxies=_proxies_dict(self.proxy))

            request.url = resp.url

            resp.raise_for_status()

            if resp.text != "":
                try:
                    result = json.loads(resp.text)
                except ValueError as json_ex:
                    LOGGER.warning(json_ex)
                    raise exceptions.SoftLayerAPIError(resp.status_code, str(resp.text))
            else:
                raise exceptions.SoftLayerAPIError(resp.status_code, "Empty response.")

            request.result = result

            if isinstance(result, list):
                return SoftLayerListResult(
                    result, int(resp.headers.get('softlayer-total-items', 0)))
            else:
                return result
        except requests.HTTPError as ex:
            try:
                message = json.loads(ex.response.text)['error']
                request.url = ex.response.url
            except ValueError as json_ex:
                if ex.response.text == "":
                    raise exceptions.SoftLayerAPIError(resp.status_code, "Empty response.")
                LOGGER.warning(json_ex)
                raise exceptions.SoftLayerAPIError(resp.status_code, ex.response.text)

            raise exceptions.SoftLayerAPIError(ex.response.status_code, message)
        except requests.RequestException as ex:
            raise exceptions.TransportError(0, str(ex))

    def print_reproduceable(self, request):
        """Prints out the minimal python code to reproduce a specific request

        The will also automatically replace the API key so its not accidently exposed.

        :param request request: Request object
        """
        command = "curl -u $SL_USER:$SL_APIKEY -X {method} -H {headers} {data} '{uri}'"

        method = REST_SPECIAL_METHODS.get(request.method)

        if method is None:
            method = 'GET'
        if request.args:
            method = 'POST'

        data = ''
        if request.payload is not None:
            data = "-d '{}'".format(request.payload)

        headers = ['"{0}: {1}"'.format(k, v) for k, v in request.transport_headers.items()]
        headers = " -H ".join(headers)
        return command.format(method=method, headers=headers, data=data, uri=request.url)


class DebugTransport(object):
    """Transport that records API call timings."""

    def __init__(self, transport):
        self.transport = transport

        #: List All API calls made during a session
        self.requests = []

    def __call__(self, call):
        call.start_time = time.time()

        self.pre_transport_log(call)
        try:
            call.result = self.transport(call)
        except (exceptions.SoftLayerAPIError, exceptions.TransportError) as ex:
            call.exception = ex

        self.post_transport_log(call)

        call.end_time = time.time()
        self.requests.append(call)

        if call.exception is not None:
            LOGGER.debug(self.print_reproduceable(call))
            raise call.exception

        return call.result

    def pre_transport_log(self, call):
        """Prints a warning before calling the API """
        output = "Calling: {})".format(call)
        LOGGER.warning(output)

    def post_transport_log(self, call):
        """Prints the result "Returned Data: \n%s" % (call.result)of an API call"""
        output = "Returned Data: \n{}".format(call.result)
        LOGGER.debug(output)

    def get_last_calls(self):
        """Returns all API calls for a session"""
        return self.requests

    def print_reproduceable(self, call):
        """Prints a reproduceable debugging output"""
        return self.transport.print_reproduceable(call)


class TimingTransport(object):
    """Transport that records API call timings."""

    def __init__(self, transport):
        self.transport = transport
        self.last_calls = []

    def __call__(self, call):
        """See Client.call for documentation."""
        start_time = time.time()

        result = self.transport(call)

        end_time = time.time()
        self.last_calls.append((call, start_time, end_time - start_time))
        return result

    def get_last_calls(self):
        """Retrieves the last_calls property.

        This property will contain a list of tuples in the form
        (Request, initiated_utc_timestamp, execution_time)
        """
        last_calls = self.last_calls
        self.last_calls = []
        return last_calls

    def print_reproduceable(self, call):
        """Not Implemented"""
        return call.service


class FixtureTransport(object):
    """Implements a transport which returns fixtures."""

    def __call__(self, call):
        """Load fixture from the default fixture path."""
        try:
            module_path = 'SoftLayer.fixtures.%s' % call.service
            module = importlib.import_module(module_path)
        except ImportError as ex:
            message = '{} fixture is not implemented'.format(call.service)
            raise NotImplementedError(message) from ex
        try:
            return getattr(module, call.method)
        except AttributeError as ex:
            message = '{}::{} fixture is not implemented'.format(call.service, call.method)
            raise NotImplementedError(message) from ex

    def print_reproduceable(self, call):
        """Not Implemented"""
        return call.service


def _proxies_dict(proxy):
    """Makes a proxy dict appropriate to pass to requests."""
    if not proxy:
        return None
    return {'http': proxy, 'https': proxy}


def _format_object_mask(objectmask):
    """Format the new style object mask.

    This wraps the user mask with mask[USER_MASK] if it does not already
    have one. This makes it slightly easier for users.

    :param objectmask: a string-based object mask

    """
    objectmask = objectmask.strip()

    if (not objectmask.startswith('mask') and
            not objectmask.startswith('[') and
            not objectmask.startswith('filteredMask')):
        objectmask = "mask[%s]" % objectmask
    return objectmask


class ComplexEncoder(json.JSONEncoder):
    """ComplexEncoder helps jsonencoder deal with byte strings"""

    def default(self, o):
        """Encodes o as JSON"""

        # Base64 encode bytes type objects.
        if isinstance(o, bytes):
            base64_bytes = base64.b64encode(o)
            return base64_bytes.decode("utf-8")
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)
