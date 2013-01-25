from SoftLayer.exceptions import SoftLayerError
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
            raise SoftLayerError(response.reason)
    except xmlrpclib.Fault, e:
        raise SoftLayerError(e.faultString)
