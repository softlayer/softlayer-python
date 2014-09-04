"""
    SoftLayer.tests.transport_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock
import requests

import SoftLayer
from SoftLayer import testing
from SoftLayer import transports


class TestXmlRpcAPICall(testing.TestCase):

    def set_up(self):
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
<value><nil/></value></member>
</struct></value>
</param>
</params>
</methodCall>
'''
        resp = transports.make_xml_rpc_api_call(
            'http://something.com/path/to/resource', 'getObject')
        args = request.call_args
        self.assertIsNotNone(args)
        args, kwargs = args

        request.assert_called_with('POST',
                                   'http://something.com/path/to/resource',
                                   headers=None,
                                   proxies=None,
                                   data=data,
                                   timeout=None)
        self.assertEqual(resp, [])

    def test_proxy_without_protocol(self):
        # NOTE(sudorandom): This used to be an instance of requests.HTTPError,
        #                   but something changes in requests to make that no
        #                   longer the case.
        self.assertRaises(
            Exception,  # NOQA
            transports.make_xml_rpc_api_call,
            'http://something.com/path/to/resource',
            'getObject',
            'localhost:3128')

    @mock.patch('requests.request')
    def test_valid_proxy(self, request):
        request.return_value = self.response
        transports.make_xml_rpc_api_call(
            'http://something.com/path/to/resource',
            'getObject',
            proxy='http://localhost:3128')
        request.assert_called_with(
            'POST',
            mock.ANY,
            headers=None,
            proxies={'https': 'http://localhost:3128',
                     'http': 'http://localhost:3128'},
            data=mock.ANY,
            timeout=None)


class TestRestAPICall(testing.TestCase):

    @mock.patch('SoftLayer.transports.requests.request')
    def test_json(self, request):
        request().content = '{}'
        resp = transports.make_rest_api_call(
            'GET', 'http://something.com/path/to/resource.json')
        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET', 'http://something.com/path/to/resource.json',
            headers=None,
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

        self.assertRaises(
            SoftLayer.SoftLayerAPIError,
            transports.make_rest_api_call,
            'GET',
            'http://something.com/path/to/resource.json')

    def test_proxy_without_protocol(self):
        self.assertRaises(
            SoftLayer.TransportError,
            transports.make_rest_api_call,
            'GET'
            'http://something.com/path/to/resource.txt',
            'localhost:3128')

    @mock.patch('SoftLayer.transports.requests.request')
    def test_valid_proxy(self, request):
        transports.make_rest_api_call(
            'GET',
            'http://something.com/path/to/resource.txt',
            proxy='http://localhost:3128')
        request.assert_called_with(
            'GET', 'http://something.com/path/to/resource.txt',
            headers=mock.ANY,
            proxies={'https': 'http://localhost:3128',
                     'http': 'http://localhost:3128'},
            timeout=None)

    @mock.patch('SoftLayer.transports.requests.request')
    def test_text(self, request):
        request().text = 'content'
        resp = transports.make_rest_api_call(
            'GET', 'http://something.com/path/to/resource.txt')
        self.assertEqual(resp, 'content')
        request.assert_called_with(
            'GET', 'http://something.com/path/to/resource.txt',
            headers=None,
            proxies=None,
            timeout=None)

        # Test Text Error
        e = requests.HTTPError('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.content = 'Error Code'
        request().raise_for_status.side_effect = e

        self.assertRaises(
            SoftLayer.SoftLayerAPIError,
            transports.make_rest_api_call,
            'GET',
            'http://something.com/path/to/resource.txt')

    @mock.patch('SoftLayer.transports.requests.request')
    def test_unknown_error(self, request):
        e = requests.RequestException('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.content = 'Error Code'
        request().raise_for_status.side_effect = e

        self.assertRaises(
            SoftLayer.TransportError,
            transports.make_rest_api_call,
            'GET',
            'http://something.com/path/to/resource.txt')
