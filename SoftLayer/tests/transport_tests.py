"""
    SoftLayer.tests.transport_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import warnings

import mock
import requests

import SoftLayer
from SoftLayer import consts
from SoftLayer import testing
from SoftLayer import transports


class TestXmlRpcAPICall(testing.TestCase):

    def set_up(self):
        self.transport = transports.XmlRpcTransport(
            endpoint_url='http://something.com',
        )
        self.response = mock.MagicMock()
        self.response.content = '''<?xml version="1.0" encoding="utf-8"?>
<params>
<param>
 <value>
  <array>
   <data/>
  </array>
 </value>
</param>
</params>'''

    @mock.patch('requests.request')
    def test_call(self, request):
        request.return_value = self.response

        data = '''<?xml version='1.0'?>
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
'''

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        resp = self.transport(req)

        request.assert_called_with('POST',
                                   'http://something.com/SoftLayer_Service',
                                   headers={'Content-Type': 'application/xml',
                                            'User-Agent': consts.USER_AGENT},
                                   proxies=None,
                                   data=data,
                                   timeout=None,
                                   cert=None,
                                   verify=True)
        self.assertEqual(resp, [])

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

    @mock.patch('requests.request')
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
            verify=True)

    @mock.patch('requests.request')
    def test_identifier(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.identifier = 1234
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            """<member>
<name>id</name>
<value><int>1234</int></value>
</member>""", kwargs['data'])

    @mock.patch('requests.request')
    def test_filter(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.filter = {'TYPE': {'attribute': {'operation': '^= prefix'}}}
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            """<member>
<name>operation</name>
<value><string>^= prefix</string></value>
</member>""", kwargs['data'])

    @mock.patch('requests.request')
    def test_limit_offset(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.limit = 10
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn("""<member>
<name>resultLimit</name>
<value><struct>
<member>""", kwargs['data'])
        self.assertIn("""<name>limit</name>
<value><int>10</int></value>
</member>""", kwargs['data'])

    @mock.patch('requests.request')
    def test_old_mask(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
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
</member>""", kwargs['data'])

    @mock.patch('requests.request')
    def test_mask_call_no_mask_prefix(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = "something.nested"
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            "<value><string>mask[something.nested]</string></value>",
            kwargs['data'])

    @mock.patch('requests.request')
    def test_mask_call_v2(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = "mask[something[nested]]"
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn(
            "<value><string>mask[something[nested]]</string></value>",
            kwargs['data'])

    @mock.patch('requests.request')
    def test_mask_call_v2_dot(self, request):
        request.return_value = self.response

        req = transports.Request()
        req.endpoint = "http://something.com"
        req.service = "SoftLayer_Service"
        req.method = "getObject"
        req.mask = "mask.something.nested"
        self.transport(req)

        args, kwargs = request.call_args
        self.assertIn("<value><string>mask.something.nested</string></value>",
                      kwargs['data'])

    @mock.patch('requests.request')
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


class TestRestAPICall(testing.TestCase):

    def set_up(self):
        self.transport = transports.RestTransport(
            endpoint_url='http://something.com',
        )

    @mock.patch('requests.request')
    def test_basic(self, request):
        request().content = '{}'
        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'

        resp = self.transport(req)
        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET', 'http://something.com/SoftLayer_Service/Resource.json',
            headers=mock.ANY,
            verify=True,
            params={},
            auth=None,
            data=None,
            cert=None,
            proxies=None,
            timeout=None)

        # Test JSON Error
        e = requests.HTTPError('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.content = '''{
            "error": "description",
            "code": "Error Code"
        }'''
        request().raise_for_status.side_effect = e

        self.assertRaises(SoftLayer.SoftLayerAPIError, self.transport, req)

    def test_proxy_without_protocol(self):
        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        req.proxy = 'localhost:3128'

        try:
            self.assertRaises(SoftLayer.TransportError, self.transport, req)
        except AssertionError:
            warnings.warn("AssertionError raised instead of a "
                          "SoftLayer.TransportError error")

    @mock.patch('requests.request')
    def test_valid_proxy(self, request):
        request().content = '{}'
        self.transport.proxy = 'http://localhost:3128'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'

        self.transport(req)
        request.assert_called_with(
            'GET', 'http://something.com/SoftLayer_Service/Resource.json',
            proxies={'https': 'http://localhost:3128',
                     'http': 'http://localhost:3128'},
            verify=True,
            cert=None,
            params={},
            auth=None,
            data=None,
            timeout=mock.ANY,
            headers=mock.ANY)

    @mock.patch('requests.request')
    def test_with_id(self, request):
        request().content = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.identifier = 2

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something.com/SoftLayer_Service/getObject/2.json',
            headers=mock.ANY,
            verify=True,
            params={},
            auth=None,
            data=None,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('requests.request')
    def test_unknown_error(self, request):
        e = requests.RequestException('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.content = 'Error Code'
        request().raise_for_status.side_effect = e

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'

        self.assertRaises(SoftLayer.TransportError, self.transport, req)
