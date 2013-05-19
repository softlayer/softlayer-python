"""
    SoftLayer.transport
    ~~~~~~~~~~~~~~~~~~~
    XML-RPC transport layer that uses the requests library.

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from SoftLayer.exceptions import (
    SoftLayerAPIError, NotWellFormed, UnsupportedEncoding, InvalidCharacter,
    SpecViolation, MethodNotFound, InvalidMethodParameters, InternalError,
    ApplicationError, RemoteSystemError, TransportError)
import xmlrpclib
import requests
import json


def make_xml_rpc_api_call(uri, method, args=None, headers=None,
                          http_headers=None, timeout=None, verbose=False):
    """ Makes a SoftLayer API call against the XML-RPC endpoint

    :param string uri: endpoint URL
    :param string method: method to call E.G.: 'getObject'
    :param dict headers: XML-RPC headers to use for the request
    :param dict http_headers: HTTP headers to use for the request
    :param int timeout: number of seconds to use as a timeout
    :param bool verbose: verbosity
    """
    if args is None:
        args = tuple()
    try:
        largs = list(args)
        largs.insert(0, {'headers': headers})

        payload = xmlrpclib.dumps(tuple(largs), methodname=method,
                                  allow_none=True)
        response = requests.post(uri, data=payload,
                                 headers=http_headers,
                                 timeout=timeout)

        response.raise_for_status()
        result = xmlrpclib.loads(response.content,)[0][0]
        return result
    except xmlrpclib.Fault, e:
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
    except requests.HTTPError, e:
        raise TransportError(e.response.status_code, str(e))
    except requests.RequestException, e:
        raise TransportError(0, str(e))


def make_rest_api_call(method, url, http_headers=None, timeout=None):
    """ Makes a SoftLayer API call against the REST endpoint

    :param string method: HTTP method: GET, POST, PUT, DELETE
    :param string url: endpoint URL
    :param dict http_headers: HTTP headers to use for the request
    :param int timeout: number of seconds to use as a timeout
    """
    resp = requests.request(method, url, headers=http_headers, timeout=timeout)
    try:
        resp.raise_for_status()
    except requests.HTTPError, e:
        if url.endswith('.json'):
            content = json.loads(e.response.content)
            raise SoftLayerAPIError(e.response.status_code, content['error'])
        else:
            raise SoftLayerAPIError(e.response.status_code, e.response.text)
    except requests.RequestException, e:
        raise TransportError(0, str(e))

    if url.endswith('.json'):
        return json.loads(resp.content)
    else:
        return resp.text
