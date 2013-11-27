"""
    SoftLayer.transports
    ~~~~~~~~~~~~~~~~~~~~
    XML-RPC transport layer that uses the requests library.

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.exceptions import (
    SoftLayerAPIError, NotWellFormed, UnsupportedEncoding, InvalidCharacter,
    SpecViolation, MethodNotFound, InvalidMethodParameters, InternalError,
    ApplicationError, RemoteSystemError, TransportError)
import xmlrpclib
import logging
import requests
import json

log = logging.getLogger(__name__)


def make_xml_rpc_api_call(uri, method, args=None, headers=None,
                          http_headers=None, timeout=None):
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

        payload = xmlrpclib.dumps(tuple(largs), methodname=method,
                                  allow_none=True)
        session = requests.Session()
        req = requests.Request('POST', uri, data=payload,
                               headers=http_headers).prepare()
        log.debug("=== REQUEST ===")
        log.info('POST %s', uri)
        log.debug(req.headers)
        log.debug(payload)

        response = session.send(req, timeout=timeout)
        log.debug("=== RESPONSE ===")
        log.debug(response.headers)
        log.debug(response.content)
        response.raise_for_status()
        result = xmlrpclib.loads(response.content,)[0][0]
        return result
    except xmlrpclib.Fault as e:
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
        raise error_mapping.get(e.faultCode, SoftLayerAPIError)(
            e.faultCode, e.faultString)
    except requests.HTTPError as e:
        raise TransportError(e.response.status_code, str(e))
    except requests.RequestException as e:
        raise TransportError(0, str(e))


def make_rest_api_call(method, url, http_headers=None, timeout=None):
    """ Makes a SoftLayer API call against the REST endpoint

    :param string method: HTTP method: GET, POST, PUT, DELETE
    :param string url: endpoint URL
    :param dict http_headers: HTTP headers to use for the request
    :param int timeout: number of seconds to use as a timeout
    """
    log.info('%s %s', method, url)
    try:
        resp = requests.request(
            method, url, headers=http_headers, timeout=timeout)
        resp.raise_for_status()
        log.debug(resp.content)
        if url.endswith('.json'):
            return json.loads(resp.content)
        else:
            return resp.text
    except requests.HTTPError as e:
        if url.endswith('.json'):
            content = json.loads(e.response.content)
            raise SoftLayerAPIError(e.response.status_code, content['error'])
        else:
            raise SoftLayerAPIError(e.response.status_code, e.response.text)
    except requests.RequestException as e:
        raise TransportError(0, str(e))
