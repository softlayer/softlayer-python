"""
    SoftLayer.tests.transport_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from mock import patch, MagicMock, ANY

from SoftLayer import SoftLayerAPIError, TransportError
from SoftLayer.transports import make_rest_api_call, make_xml_rpc_api_call
from SoftLayer.tests import unittest
from requests import HTTPError, RequestException


class TestXmlRpcAPICall(unittest.TestCase):

    @patch('SoftLayer.transports.requests.Session.send')
    def test_call(self, send):
        send().content = '''<?xml version="1.0" encoding="utf-8"?>
<params>
<param>
 <value>
  <array>
   <data/>
  </array>
 </value>
</param>
</params>
'''

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
        resp = make_xml_rpc_api_call(
            'http://something.com/path/to/resource', 'getObject')
        args = send.call_args
        self.assertIsNotNone(args)
        args, kwargs = args

        send.assert_called_with(ANY, timeout=None)
        self.assertEqual(resp, [])
        self.assertEquals(args[0].body, data)


class TestRestAPICall(unittest.TestCase):

    @patch('SoftLayer.transports.requests.request')
    def test_json(self, request):
        request().content = '{}'
        resp = make_rest_api_call(
            'GET', 'http://something.com/path/to/resource.json')
        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET', 'http://something.com/path/to/resource.json',
            headers=None,
            timeout=None)

        # Test JSON Error
        e = HTTPError('error')
        e.response = MagicMock()
        e.response.status_code = 404
        e.response.content = '''{
            "error": "description",
            "code": "Error Code"
        }'''
        request().raise_for_status.side_effect = e

        self.assertRaises(
            SoftLayerAPIError,
            make_rest_api_call,
            'GET',
            'http://something.com/path/to/resource.json')

    @patch('SoftLayer.transports.requests.request')
    def test_text(self, request):
        request().text = 'content'
        resp = make_rest_api_call(
            'GET', 'http://something.com/path/to/resource.txt')
        self.assertEqual(resp, 'content')
        request.assert_called_with(
            'GET', 'http://something.com/path/to/resource.txt',
            headers=None,
            timeout=None)

        # Test Text Error
        e = HTTPError('error')
        e.response = MagicMock()
        e.response.status_code = 404
        e.response.content = 'Error Code'
        request().raise_for_status.side_effect = e

        self.assertRaises(
            SoftLayerAPIError,
            make_rest_api_call,
            'GET',
            'http://something.com/path/to/resource.txt')

    @patch('SoftLayer.transports.requests.request')
    def test_unknown_error(self, request):
        e = RequestException('error')
        e.response = MagicMock()
        e.response.status_code = 404
        e.response.content = 'Error Code'
        request().raise_for_status.side_effect = e

        self.assertRaises(
            TransportError,
            make_rest_api_call,
            'GET',
            'http://something.com/path/to/resource.txt')
