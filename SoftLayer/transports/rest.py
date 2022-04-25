"""
    SoftLayer.transports.rest
    ~~~~~~~~~~~~~~~~~~~~
    REST Style transport library

    :license: MIT, see LICENSE for more details.
"""

import json
import logging
import requests

from SoftLayer import consts
from SoftLayer import exceptions

from .transport import _format_object_mask
from .transport import _proxies_dict
from .transport import ComplexEncoder
from .transport import get_session
from .transport import SoftLayerListResult

REST_SPECIAL_METHODS = {
    # 'deleteObject': 'DELETE',
    'createObject': 'POST',
    'createObjects': 'POST',
    'editObject': 'PUT',
    'editObjects': 'PUT',
}


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
        self.logger = logging.getLogger(__name__)

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
                    self.logger.warning(json_ex)
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
                self.logger.warning(json_ex)
                raise exceptions.SoftLayerAPIError(resp.status_code, ex.response.text)

            raise exceptions.SoftLayerAPIError(ex.response.status_code, message)
        except requests.RequestException as ex:
            raise exceptions.TransportError(0, str(ex))

    @staticmethod
    def print_reproduceable(request):
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
