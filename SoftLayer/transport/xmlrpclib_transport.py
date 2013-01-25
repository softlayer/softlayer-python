from SoftLayer.consts import USER_AGENT
from SoftLayer.exceptions import SoftLayerError
from urlparse import urlparse
import xmlrpclib

import socket


def make_api_call(uri, method, args, headers=None, http_headers=None,
                  timeout=None, verbose=False):
    http_protocol = urlparse(uri).scheme

    if http_protocol == "https":
        transport = SecureProxyTransport()
    else:
        transport = ProxyTransport()

    if http_headers:
        for name, value in http_headers.items():
            transport.set_raw_header(name, value)

    __prevDefaultTimeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(timeout)
        proxy = xmlrpclib.ServerProxy(uri, transport=transport,
                                      verbose=verbose, allow_none=True)
        return getattr(proxy, method)({'headers': headers}, *args)
    except xmlrpclib.Fault, e:
        raise SoftLayerError(e.faultString)
    finally:
        socket.setdefaulttimeout(__prevDefaultTimeout)


class ProxyTransport(xmlrpclib.Transport):
    user_agent = USER_AGENT
    __extra_headers = None

    def set_raw_header(self, name, value):
        if self.__extra_headers is None:
            self.__extra_headers = {}
        self.__extra_headers[name] = value

    def send_user_agent(self, connection):
        if self.__extra_headers:
            for k, v in self.__extra_headers.iteritems():
                connection.putheader(k, v)


class SecureProxyTransport(xmlrpclib.SafeTransport, ProxyTransport):
    user_agent = USER_AGENT
    __extra_headers = {}
