from SoftLayer.consts import USER_AGENT
import xmlrpclib


class ProxyTransport(xmlrpclib.Transport):
    user_agent = USER_AGENT
    __extra_headers = None

    def set_raw_header(self, name, value):
        if self.__extra_headers is None:
            self.__extra_headers = {}
        self.__extra_headers[name] = value
    def send_user_agent(self, connection):
        connection.putheader("User-Agent", self.user_agent)
        if self.__extra_headers:
            for k, v in self.__extra_headers.iteritems():
                connection.putheader(k, v)


class SecureProxyTransport(xmlrpclib.SafeTransport, ProxyTransport):
    user_agent = USER_AGENT
    __extra_headers = {}
