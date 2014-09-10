"""
    SoftLayer.transports
    ~~~~~~~~~~~~~~~~~~~~
    XML-RPC transport layer that uses the requests library.

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer import utils

import json
import logging

import requests

LOGGER = logging.getLogger(__name__)


def _proxies_dict(proxy):
    """Makes a dict appropriate to pass to requests."""
    if not proxy:
        return None
    return {'http': proxy, 'https': proxy}


def make_xml_rpc_api_call(url, method, args=None, headers=None,
                          http_headers=None, timeout=None, proxy=None,
                          verify=True, cert=None):
    """Makes a SoftLayer API call against the XML-RPC endpoint.

    :param string uri: endpoint URL
    :param string method: method to call E.G.: 'getObject'
    :param dict headers: XML-RPC headers to use for the request
    :param dict http_headers: HTTP headers to use for the request
    :param int timeout: number of seconds to use as a timeout
    :param bool verify: verify SSL cert
    :param cert: client certificate path
    """
    if args is None:
        args = tuple()
    try:
        largs = list(args)
        largs.insert(0, {'headers': headers})

        payload = utils.xmlrpc_client.dumps(tuple(largs),
                                            methodname=method,
                                            allow_none=True)
        LOGGER.debug("=== REQUEST ===")
        LOGGER.info('POST %s', url)
        LOGGER.debug(http_headers)
        LOGGER.debug(payload)

        response = requests.request('POST', url,
                                    data=payload,
                                    headers=http_headers,
                                    timeout=timeout,
                                    verify=verify,
                                    cert=cert,
                                    proxies=_proxies_dict(proxy))
        LOGGER.debug("=== RESPONSE ===")
        LOGGER.debug(response.headers)
        LOGGER.debug(response.content)
        response.raise_for_status()
        result = utils.xmlrpc_client.loads(response.content,)[0][0]
        return result
    except utils.xmlrpc_client.Fault as ex:
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
        raise error_mapping.get(ex.faultCode, exceptions.SoftLayerAPIError)(
            ex.faultCode, ex.faultString)
    except requests.HTTPError as ex:
        raise exceptions.TransportError(ex.response.status_code, str(ex))
    except requests.RequestException as ex:
        raise exceptions.TransportError(0, str(ex))


def make_rest_api_call(method, url,
                       http_headers=None, timeout=None, proxy=None):
    """Makes a SoftLayer API call against the REST endpoint.

    :param string method: HTTP method: GET, POST, PUT, DELETE
    :param string url: endpoint URL
    :param dict http_headers: HTTP headers to use for the request
    :param int timeout: number of seconds to use as a timeout
    """
    LOGGER.debug("=== REQUEST ===")
    LOGGER.info('%s %s', method, url)
    LOGGER.debug(http_headers)
    try:
        resp = requests.request(method, url,
                                headers=http_headers,
                                timeout=timeout,
                                proxies=_proxies_dict(proxy))
        LOGGER.debug("=== RESPONSE ===")
        LOGGER.debug(resp.headers)
        LOGGER.debug(resp.content)
        resp.raise_for_status()
        if url.endswith('.json'):
            return json.loads(resp.content)
        else:
            return resp.text
    except requests.HTTPError as ex:
        if url.endswith('.json'):
            content = json.loads(ex.response.content)
            raise exceptions.SoftLayerAPIError(ex.response.status_code,
                                               content['error'])
        else:
            raise exceptions.SoftLayerAPIError(ex.response.status_code,
                                               ex.response.text)
    except requests.RequestException as ex:
        raise exceptions.TransportError(0, str(ex))
