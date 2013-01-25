
try:
    from SoftLayer.transport.requests_transport import make_api_call
except ImportError:
    from SoftLayer.transport.xmlrpclib_transport import make_api_call
