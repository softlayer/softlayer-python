"""
    SoftLayer.testing.xmlrpc
    ~~~~~~~~~~~~~~~~~~~~~~~~
    XMP-RPC server which can use a transport to proxy requests for testing.

    If you want to spin up a test XML server to make fake API calls with, try this:

    quick-server.py
    ---
    import SoftLayer
    from SoftLayer.testing import xmlrpc

    my_xport = SoftLayer.FixtureTransport()
    my_server = xmlrpc.create_test_server(my_xport, "localhost", port=4321)
    print(f"Server running on http://{my_server.server_name}:{my_server.server_port}")
    ---
    $> python quick-server.py
    $> curl -X POST -d "<?xml version='1.0' encoding='iso-8859-1'?><methodCall><methodName> \
getInvoiceTopLevelItems</methodName><params><param><value><struct><member><name>headers</name> \
<value><struct><member><name>SoftLayer_Billing_InvoiceInitParameters</name><value><struct> \
<member><name>id</name><value><string>1234</string></value></member></struct></value></member> \
</struct></value></member></struct></value></param></params></methodCall>" \
http://127.0.0.1:4321/SoftLayer_Billing_Invoice

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


class TestServer(http.server.ThreadingHTTPServer):
    """Test HTTP server which holds a given transport."""

    def __init__(self, transport, *args, **kw):
        http.server.ThreadingHTTPServer.__init__(self, *args, **kw)
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
            req.identifier = _item_by_key_postfix(headers, 'InitParameters').get('id')
            req.transport_headers = dict(((k.lower(), v) for k, v in self.headers.items()))
            req.headers = headers

            # Get response
            response = self.server.transport(req)

            # Need to convert BACK to list, so xmlrpc can dump it out properly.
            if isinstance(response, SoftLayer.transports.transport.SoftLayerListResult):
                response = list(response)
            response_body = xmlrpc.client.dumps((response,), allow_none=True, methodresponse=True)

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
            response_body = xmlrpc.client.dumps(response, allow_none=True, methodresponse=True)
            self.wfile.write(response_body.encode('utf-8'))

        except SoftLayer.SoftLayerAPIError as ex:
            self.send_response(200)
            self.end_headers()
            response = xmlrpc.client.Fault(ex.faultCode, str(ex.reason))
            response_body = xmlrpc.client.dumps(response, allow_none=True, methodresponse=True)
            self.wfile.write(response_body.encode('utf-8'))
        except OverflowError as ex:
            self.send_response(555)
            self.send_header("Content-type", "application/xml; charset=UTF-8")
            self.end_headers()
            response_body = '''<error>OverflowError in XML response.</error>'''
            self.wfile.write(response_body.encode('utf-8'))
            logging.exception("Error while handling request: %s", ex)
        except Exception as ex:
            self.send_response(500)
            logging.exception("Error while handling request: %s", ex)

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
    thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01})
    thread.start()
    return server
