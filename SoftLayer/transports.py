"""
    SoftLayer.transports
    ~~~~~~~~~~~~~~~~~~~~
    XML-RPC transport layer that uses the requests library.

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.exceptions import (
    SoftLayerAPIError, NotWellFormed, UnsupportedEncoding, InvalidCharacter,
    SpecViolation, MethodNotFound, InvalidMethodParameters, InternalError,
    ApplicationError, RemoteSystemError, TransportError)
from SoftLayer.utils import xmlrpc_client

import logging
import requests
import json

LOGGER = logging.getLogger(__name__)


def _proxies_dict(proxy):
    """ Makes a dict appropriate to pass to requests """
    if not proxy:
        return None
    return {'http': proxy, 'https': proxy}


def make_xml_rpc_api_call(uri, method, args=None, headers=None,
                          http_headers=None, timeout=None, proxy=None):
    """ Makes a SoftLayer API call against the XML-RPC endpoint

    :param string uri: endpoint URL
    :param string method: method to call E.G.: 'getObject'
    :param dict headers: XML-RPC headers to use for the request
    :param dict http_headers: HTTP headers to use for the request
    :param int timeout: number of seconds to use as a timeout
    """
    if args is None:
        args = tuple()
    try:
        largs = list(args)
        largs.insert(0, {'headers': headers})

        payload = xmlrpc_client.dumps(tuple(largs),
                                      methodname=method,
                                      allow_none=True)
        session = requests.Session()
        req = requests.Request('POST', uri, data=payload,
                               headers=http_headers).prepare()
        LOGGER.debug("=== REQUEST ===")
        LOGGER.info('POST %s', uri)
        LOGGER.debug(req.headers)
        LOGGER.debug(payload)

        response = session.send(req,
                                timeout=timeout,
                                proxies=_proxies_dict(proxy))
        LOGGER.debug("=== RESPONSE ===")
        LOGGER.debug(response.headers)
        LOGGER.debug(response.content)
        response.raise_for_status()
        result = xmlrpc_client.loads(response.content,)[0][0]
        return result
    except xmlrpc_client.Fault as ex:
        # These exceptions are formed from the XML-RPC spec
        # http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php
        error_mapping = {
            '-32700': NotWellFormed,
            '-32701': UnsupportedEncoding,
            '-32702': InvalidCharacter,
            '-32600': SpecViolation,
            '-32601': MethodNotFound,
            '-32602': InvalidMethodParameters,
            '-32603': InternalError,
            '-32500': ApplicationError,
            '-32400': RemoteSystemError,
            '-32300': TransportError,
        }
        raise error_mapping.get(ex.faultCode, SoftLayerAPIError)(
            ex.faultCode, ex.faultString)
    except requests.HTTPError as ex:
        raise TransportError(ex.response.status_code, str(ex))
    except requests.RequestException as ex:
        raise TransportError(0, str(ex))


def make_rest_api_call(method, url,
                       http_headers=None, timeout=None, proxy=None):
    """ Makes a SoftLayer API call against the REST endpoint

    :param string method: HTTP method: GET, POST, PUT, DELETE
    :param string url: endpoint URL
    :param dict http_headers: HTTP headers to use for the request
    :param int timeout: number of seconds to use as a timeout
    """
    LOGGER.info('%s %s', method, url)
    try:
        resp = requests.request(method, url,
                                headers=http_headers,
                                timeout=timeout,
                                proxies=_proxies_dict(proxy))
        resp.raise_for_status()
        LOGGER.debug(resp.content)
        if url.endswith('.json'):
            return json.loads(resp.content)
        else:
            return resp.text
    except requests.HTTPError as ex:
        if url.endswith('.json'):
            content = json.loads(ex.response.content)
            raise SoftLayerAPIError(ex.response.status_code, content['error'])
        else:
            raise SoftLayerAPIError(ex.response.status_code, ex.response.text)
    except requests.RequestException as ex:
        raise TransportError(0, str(ex))
