from SoftLayer.exceptions import (
    SoftLayerAPIError, NotWellFormed, UnsupportedEncoding, InvalidCharacter,
    SpecViolation, MethodNotFound, InvalidMethodParameters, InternalError,
    ApplicationError, RemoteSystemError, TransportError)
import xmlrpclib
import requests


def make_api_call(uri, method, args, headers=None,
                  http_headers=None, timeout=None, verbose=False):
    try:
        largs = list(args)
        largs.insert(0, {'headers': headers})

        payload = xmlrpclib.dumps(tuple(largs), methodname=method,
                                  allow_none=True)
        
        response = requests.post(uri, data=payload,
                                 headers=http_headers,
                                 timeout=timeout)

        if response.status_code == 200:
            result = xmlrpclib.loads(response.content,)[0][0]
            return result
        else:
            # Some error occurred
            raise SoftLayerAPIError(response.status_code, response.reason)
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
