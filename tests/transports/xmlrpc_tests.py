"""
    SoftLayer.tests.transports.xmlrc
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import io
from unittest import mock as mock
import warnings

import pytest
import requests

import SoftLayer
from SoftLayer import consts
from SoftLayer import testing
from SoftLayer import transports


def get_xmlrpc_response():
    response = requests.Response()
    list_body = b'''<?xml version="1.0" encoding="utf-8"?>
<params>
<param>
<value>
<array>
<data/>
</array>
</value>
</param>
</params>'''
    response.raw = io.BytesIO(list_body)
    response.headers['SoftLayer-Total-Items'] = 10
    response.status_code = 200
    return response


class TestXmlRpcAPICall(testing.TestCase):

    def set_up(self):
        self.transport = transports.XmlRpcTransport(
            endpoint_url='http://something9999999999999999999999.com',
        )
        self.response = get_xmlrpc_response()

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_call(self, request):
        request.return_value = self.response

        data = '''<?xml version='1.0' encoding='iso-8859-1'?>
<methodCall>
<methodName>getObject</methodName>
<params>
<param>
<value><struct>
<member>
<name>headers</name>
<value><struct>
</struct></value>
</member>
</struct></value>
</param>
</params>
</methodCall>
'''.encode()

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        resp = self.transport(req)

        request.assert_called_with('POST',
                                   'http://something9999999999999999999999.com/SoftLayer_Service',
                                   headers={'Content-Type': 'application/xml',
                                            'User-Agent': consts.USER_AGENT},
                                   proxies=None,
                                   data=data,
                                   timeout=None,
                                   cert=None,
                                   verify=True,
                                   auth=None)
        self.assertEqual(resp, [])
        self.assertIsInstance(resp, transports.SoftLayerListResult)
        self.assertEqual(resp.total_count, 10)

    def test_proxy_without_protocol(self):
        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        req.proxy = 'localhost:3128'

        try:
            self.assertRaises(SoftLayer.TransportError, self.transport, req)
        except AssertionError:
            warnings.warn("Incorrect Exception raised. Expected a "
                          "SoftLayer.TransportError error")

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_valid_proxy(self, request):
        request.return_value = self.response
        self.transport.proxy = 'http://localhost:3128'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        self.transport(req)

        request.assert_called_with(
            'POST',
            mock.ANY,
            proxies={'https': 'http://localhost:3128',
                     'http': 'http://localhost:3128'},
            data=mock.ANY,
            headers=mock.ANY,
            timeout=None,
            cert=None,
            verify=True,
            auth=None)

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_identifier(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something9999999999999999999999.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.identifier = 1234
        self.transport(req)

        _, kwargs = request.call_args
        self.assertIn(
            """<member>
<name>id</name>
<value><int>1234</int></value>
</member>""".encode(), kwargs['data'])

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_filter(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something9999999999999999999999.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.filter = {'TYPE': {'attribute': {'operation': '^= prefix'}}}
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            """<member>
<name>operation</name>
<value><string>^= prefix</string></value>
</member>""".encode(), kwargs['data'])

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_limit_offset(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something9999999999999999999999.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.limit = 10
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn("""<member>
<name>resultLimit</name>
<value><struct>
<member>""".encode(), kwargs['data'])
        self.assertIn("""<name>limit</name>
<value><int>10</int></value>
</member>""".encode(), kwargs['data'])

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_old_mask(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something9999999999999999999999.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = {"something": "nested"}
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn("""<member>
<name>mask</name>
<value><struct>
<member>
<name>something</name>
<value><string>nested</string></value>
</member>
</struct></value>
</member>""".encode(), kwargs['data'])

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_mask_call_no_mask_prefix(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something9999999999999999999999.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = "something.nested"
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            "<value><string>mask[something.nested]</string></value>".encode(),
            kwargs['data'])

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_mask_call_v2(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something9999999999999999999999.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = "mask[something[nested]]"
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            "<value><string>mask[something[nested]]</string></value>".encode(),
            kwargs['data'])

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_mask_call_filteredMask(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something9999999999999999999999.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = "filteredMask[something[nested]]"
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            "<value><string>filteredMask[something[nested]]</string></value>".encode(),
            kwargs['data'])

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_mask_call_v2_dot(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something9999999999999999999999.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = "mask.something.nested"
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn("<value><string>mask.something.nested</string></value>".encode(),
                      kwargs['data'])

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_request_exception(self, request):
        # Test Text Error
        e = requests.HTTPError('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.content = 'Error Code'
        request().raise_for_status.side_effect = e

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'

        self.assertRaises(SoftLayer.TransportError, self.transport, req)

    def test_print_reproduceable(self):
        req = transports.Request()
        req.url = "https://test.com"
        req.payload = "testing"
        req.transport_headers = {"test-headers": 'aaaa'}
        output_text = self.transport.print_reproduceable(req)
        self.assertIn("https://test.com", output_text)

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    @mock.patch('requests.auth.HTTPBasicAuth')
    def test_ibm_id_call(self, auth, request):
        request.return_value = self.response

        data = '''<?xml version='1.0' encoding='iso-8859-1'?>
<methodCall>
<methodName>getObject</methodName>
<params>
<param>
<value><struct>
<member>
<name>headers</name>
<value><struct>
</struct></value>
</member>
</struct></value>
</param>
</params>
</methodCall>
'''.encode()

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.transport_user = 'apikey'
        req.transport_password = '1234567890qweasdzxc'
        resp = self.transport(req)

        auth.assert_called_with('apikey', '1234567890qweasdzxc')
        request.assert_called_with('POST',
                                   'http://something9999999999999999999999.com/SoftLayer_Service',
                                   headers={'Content-Type': 'application/xml',
                                            'User-Agent': consts.USER_AGENT},
                                   proxies=None,
                                   data=data,
                                   timeout=None,
                                   cert=None,
                                   verify=True,
                                   auth=mock.ANY)
        self.assertEqual(resp, [])
        self.assertIsInstance(resp, transports.SoftLayerListResult)
        self.assertEqual(resp.total_count, 10)

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_call_large_number_response(self, request):
        response = requests.Response()
        body = b'''<?xml version="1.0" encoding="utf-8"?>
<params>
<param>
 <value>
  <array>
   <data>
    <value>
     <struct>
      <member>
       <name>bytesUsed</name>
       <value><int>2666148982056</int></value>
      </member>
     </struct>
    </value>
   </data>
  </array>
 </value>
</param>
</params>
        '''
        response.raw = io.BytesIO(body)
        response.headers['SoftLayer-Total-Items'] = 1
        response.status_code = 200
        request.return_value = response

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        resp = self.transport(req)
        self.assertEqual(resp[0]['bytesUsed'], 2666148982056)

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_nonascii_characters(self, request):
        request.return_value = self.response
        hostname = 'testé'
        data = '''<?xml version='1.0' encoding='iso-8859-1'?>
<methodCall>
<methodName>getObject</methodName>
<params>
<param>
<value><struct>
<member>
<name>headers</name>
<value><struct>
</struct></value>
</member>
</struct></value>
</param>
<param>
<value><struct>
<member>
<name>hostname</name>
<value><string>testé</string></value>
</member>
</struct></value>
</param>
</params>
</methodCall>
'''.encode()

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.args = ({'hostname': hostname},)
        req.transport_user = "testUser"
        req.transport_password = "testApiKey"
        resp = self.transport(req)

        request.assert_called_with('POST',
                                   'http://something9999999999999999999999.com/SoftLayer_Service',
                                   headers={'Content-Type': 'application/xml',
                                            'User-Agent': consts.USER_AGENT},
                                   proxies=None,
                                   data=data,
                                   timeout=None,
                                   cert=None,
                                   verify=True,
                                   auth=mock.ANY)
        self.assertEqual(resp, [])
        self.assertIsInstance(resp, transports.SoftLayerListResult)
        self.assertEqual(resp.total_count, 10)


@mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
@pytest.mark.parametrize(
    "transport_verify,request_verify,expected",
    [
        (True, True, True),
        (True, False, False),
        (True, None, True),

        (False, True, True),
        (False, False, False),
        (False, None, False),

        (None, True, True),
        (None, False, False),
        (None, None, True),
    ]
)
def test_verify(request,
                transport_verify,
                request_verify,
                expected):
    request.return_value = get_xmlrpc_response()

    transport = transports.XmlRpcTransport(
        endpoint_url='http://something9999999999999999999999.com',
    )

    req = transports.Request()
    req.service = 'SoftLayer_Service'
    req.method = 'getObject'

    if request_verify is not None:
        req.verify = request_verify

    if transport_verify is not None:
        transport.verify = transport_verify

    transport(req)

    request.assert_called_with('POST',
                               'http://something9999999999999999999999.com/SoftLayer_Service',
                               data=mock.ANY,
                               headers=mock.ANY,
                               cert=mock.ANY,
                               proxies=mock.ANY,
                               timeout=mock.ANY,
                               verify=expected,
                               auth=None)
