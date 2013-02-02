from SoftLayer.exceptions import (
    SoftLayerAPIError, NotWellFormed, UnsupportedEncoding, InvalidCharacter,
    SpecViolation, MethodNotFound, InvalidMethodParameters, InternalError,
    ApplicationError, RemoteSystemError, TransportError)
import xmlrpclib
import requests


def make_api_call(uri, method, args=None, headers=None,
                  http_headers=None, timeout=None, verbose=False):
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
