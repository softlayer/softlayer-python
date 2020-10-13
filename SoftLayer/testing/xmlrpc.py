"""
    SoftLayer.testing.xmlrpc
    ~~~~~~~~~~~~~~~~~~~~~~~~
    XMP-RPC server which can use a transport to proxy requests for testing.

    :license: MIT, see LICENSE for more details.
"""
import http.server
import logging
import threading
import xmlrpc.client

import SoftLayer
from SoftLayer import transports
from SoftLayer import utils

# pylint: disable=invalid-name, broad-except, arguments-differ


class TestServer(http.server.HTTPServer):
    """Test HTTP server which holds a given transport."""

    def __init__(self, transport, *args, **kw):
        http.server.HTTPServer.__init__(self, *args, **kw)
        self.transport = transport


class TestHandler(http.server.BaseHTTPRequestHandler):
    """Test XML-RPC Handler which converts XML-RPC to transport requests."""

    def do_POST(self):
        """Handle XML-RPC POSTs."""
        try:
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length).decode('utf-8')
            args, method = xmlrpc.client.loads(data)
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

            response_body = xmlrpc.client.dumps((response,),
                                                allow_none=True,
                                                methodresponse=True)

            self.send_response(200)
            self.send_header("Content-type", "application/xml; charset=UTF-8")
            self.end_headers()
            try:
                self.wfile.write(response_body.encode('utf-8'))
            except UnicodeDecodeError:
                self.wfile.write(response_body)

        except (NotImplementedError, NameError) as ex:
            self.send_response(200)
            self.end_headers()
            response = xmlrpc.client.Fault(404, str(ex))
            response_body = xmlrpc.client.dumps(response,
                                                allow_none=True,
                                                methodresponse=True)
            self.wfile.write(response_body.encode('utf-8'))

        except SoftLayer.SoftLayerAPIError as ex:
            self.send_response(200)
            self.end_headers()
            response = xmlrpc.client.Fault(ex.faultCode, str(ex.reason))
            response_body = xmlrpc.client.dumps(response,
                                                allow_none=True,
                                                methodresponse=True)
            self.wfile.write(response_body.encode('utf-8'))
        except Exception:
            self.send_response(500)
            logging.exception("Error while handling request")

    def log_message(self, fmt, *args):
        """Override log_message."""


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
