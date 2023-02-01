"""
    SoftLayer.transports.xmlrpc
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    XML-RPC Style transport library

    :license: MIT, see LICENSE for more details.
"""
import re
from string import Template
import xmlrpc.client

import requests

from SoftLayer import consts
from SoftLayer import exceptions

from .transport import _format_object_mask
from .transport import _proxies_dict
from .transport import get_session
from .transport import SoftLayerListResult


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
                                              allow_none=True,
                                              encoding="iso-8859-1")

        # Prefer the request setting, if it's not None
        verify = request.verify
        if verify is None:
            request.verify = self.verify

        try:
            resp = self.client.request('POST', request.url,
                                       data=request.payload.encode(),
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
payload = $payload
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
        safe_payload = safe_payload.encode()
        substitutions = {"url": request.url, "payload": safe_payload, "transport_headers": request.transport_headers,
                         "timeout": self.timeout, "verify": request.verify, "cert": request.cert,
                         "proxy": _proxies_dict(self.proxy)}
        return output.substitute(substitutions)
