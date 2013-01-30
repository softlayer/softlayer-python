
try:
    from SoftLayer.transport.requests_transport import make_api_call
except ImportError:  # pragma: no cover
    from SoftLayer.transport.xmlrpclib_transport import make_api_call
