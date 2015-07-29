"""
    SoftLayer.testing.xmlrpc
    ~~~~~~~~~~~~~~~~~~~~~~~~
    XMP-RPC server which can use a transport to proxy requests for testing.

    :license: MIT, see LICENSE for more details.
"""
import logging
import threading

import six

import SoftLayer
from SoftLayer import transports
from SoftLayer import utils

# pylint: disable=invalid-name, broad-except


class TestServer(six.moves.BaseHTTPServer.HTTPServer):
    """Test HTTP server which holds a given transport."""

    def __init__(self, transport, *args, **kw):
        six.moves.BaseHTTPServer.HTTPServer.__init__(self, *args, **kw)
        self.transport = transport


class TestHandler(six.moves.BaseHTTPServer.BaseHTTPRequestHandler):
    """Test XML-RPC Handler which converts XML-RPC to transport requests."""

    def do_POST(self):
        """Handle XML-RPC POSTs."""
        try:
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length).decode('utf-8')
            args, method = utils.xmlrpc_client.loads(data)
            headers = args[0].get('headers', {})

            # Form Request for the transport
            req = transports.Request()
            req.service = self.path.lstrip('/')
            req.method = method
            req.limit = utils.lookup(headers, 'resultLimit', 'limit')
            req.offset = utils.lookup(headers, 'resultLimit', 'offset')
            req.args = args[1:]
            req.filter = _item_by_key_postfix(headers, 'ObjectFilter') or None
            req.mask = _item_by_key_postfix(headers, 'ObjectMask').get('mask')
            req.identifier = _item_by_key_postfix(headers,
                                                  'InitParameters').get('id')
            req.transport_headers = dict(((k.lower(), v)
                                          for k, v in self.headers.items()))
            req.headers = headers

            # Get response
            response = self.server.transport(req)

            response_body = utils.xmlrpc_client.dumps((response,),
                                                      allow_none=True,
                                                      methodresponse=True)

            self.send_response(200)
            self.send_header("Content-type", "application/xml")
            self.end_headers()
            self.wfile.write(response_body.encode('utf-8'))

        except SoftLayer.SoftLayerAPIError as ex:
            self.send_response(200)
            self.end_headers()
            response = utils.xmlrpc_client.Fault(ex.faultCode, str(ex.reason))
            response_body = utils.xmlrpc_client.dumps(response,
                                                      allow_none=True,
                                                      methodresponse=True)
            self.wfile.write(response_body.encode('utf-8'))
        except Exception as ex:
            self.send_response(500)
            logging.exception("Error while handling request")

    def log_message(self, fmt, *args):
        """Override log_message."""
        pass


def _item_by_key_postfix(dictionary, key_prefix):
    """Get item from a dictionary which begins with the given prefix."""
    for key, value in dictionary.items():
        if key.endswith(key_prefix):
            return value

    return {}


def create_test_server(transport, host='localhost', port=0):
    """Create a test XML-RPC server in a new thread."""
    server = TestServer(transport, (host, port), TestHandler)
    thread = threading.Thread(target=server.serve_forever,
                              kwargs={'poll_interval': 0.01})
    thread.start()
    return server
