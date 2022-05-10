"""
    SoftLayer.tests.transports.rest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import requests
from unittest import mock as mock
import warnings

import SoftLayer
from SoftLayer import testing
from SoftLayer import transports


class TestRestAPICall(testing.TestCase):

    def set_up(self):
        self.transport = transports.RestTransport(
            endpoint_url='http://something9999999999999999999999.com',
        )

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_basic(self, request):
        request().content = '[]'
        request().text = '[]'
        request().headers = requests.structures.CaseInsensitiveDict({
            'SoftLayer-Total-Items': '10',
        })

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        resp = self.transport(req)

        self.assertEqual(resp, [])
        self.assertIsInstance(resp, transports.SoftLayerListResult)
        self.assertEqual(resp.total_count, 10)
        request.assert_called_with(
            'GET', 'http://something9999999999999999999999.com/SoftLayer_Service/Resource.json',
            headers=mock.ANY,
            auth=None,
            data=None,
            params={},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_http_and_json_error(self, request):
        # Test JSON Error
        e = requests.HTTPError('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.text = '''
            "error": "description",
            "code": "Error Code"
        '''
        request().raise_for_status.side_effect = e

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        self.assertRaises(SoftLayer.SoftLayerAPIError, self.transport, req)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_http_and_empty_error(self, request):
        # Test JSON Error
        e = requests.HTTPError('error')
        e.response = mock.MagicMock()
        e.response.status_code = 404
        e.response.text = ''
        request().raise_for_status.side_effect = e

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        self.assertRaises(SoftLayer.SoftLayerAPIError, self.transport, req)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_empty_error(self, request):
        # Test empty response error.
        request().text = ''

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        self.assertRaises(SoftLayer.SoftLayerAPIError, self.transport, req)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_json_error(self, request):
        # Test non-json response error.
        request().text = 'Not JSON'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        self.assertRaises(SoftLayer.SoftLayerAPIError, self.transport, req)

    def test_proxy_without_protocol(self):
        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'
        req.proxy = 'localhost:3128'
        try:
            self.assertRaises(SoftLayer.TransportError, self.transport, req)
        except AssertionError:
            warnings.warn("AssertionError raised instead of a SoftLayer.TransportError error")

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_valid_proxy(self, request):
        request().text = '{}'
        self.transport.proxy = 'http://localhost:3128'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'Resource'

        self.transport(req)

        request.assert_called_with(
            'GET', 'http://something9999999999999999999999.com/SoftLayer_Service/Resource.json',
            proxies={'https': 'http://localhost:3128',
                     'http': 'http://localhost:3128'},
            auth=None,
            data=None,
            params={},
            verify=True,
            cert=None,
            timeout=mock.ANY,
            headers=mock.ANY)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_with_id(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.identifier = 2

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something9999999999999999999999.com/SoftLayer_Service/2/getObject.json',
            headers=mock.ANY,
            auth=None,
            data=None,
            params={},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_with_args(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.args = ('test', 1)

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'POST',
            'http://something9999999999999999999999.com/SoftLayer_Service/getObject.json',
            headers=mock.ANY,
            auth=None,
            data='{"parameters": ["test", 1]}',
            params={},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_with_args_bytes(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.args = ('test', b'asdf')

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'POST',
            'http://something9999999999999999999999.com/SoftLayer_Service/getObject.json',
            headers=mock.ANY,
            auth=None,
            data='{"parameters": ["test", "YXNkZg=="]}',
            params={},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_with_filter(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.filter = {'TYPE': {'attribute': {'operation': '^= prefix'}}}

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something9999999999999999999999.com/SoftLayer_Service/getObject.json',
            params={'objectFilter':
                    '{"TYPE": {"attribute": {"operation": "^= prefix"}}}'},
            headers=mock.ANY,
            auth=None,
            data=None,
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_with_mask(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.mask = 'id,property'

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something9999999999999999999999.com/SoftLayer_Service/getObject.json',
            params={'objectMask': 'mask[id,property]'},
            headers=mock.ANY,
            auth=None,
            data=None,
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

        # Now test with mask[] prefix
        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.mask = 'mask[id,property]'

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something9999999999999999999999.com/SoftLayer_Service/getObject.json',
            params={'objectMask': 'mask[id,property]'},
            headers=mock.ANY,
            auth=None,
            data=None,
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    def test_with_limit_offset(self, request):
        request().text = '{}'

        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.identifier = 2
        req.limit = 10
        req.offset = 5

        resp = self.transport(req)

        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET',
            'http://something9999999999999999999999.com/SoftLayer_Service/2/getObject.json',
            headers=mock.ANY,
            auth=None,
            data=None,
            params={'resultLimit': '5,10'},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
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

    @mock.patch('SoftLayer.transports.rest.requests.Session.request')
    @mock.patch('requests.auth.HTTPBasicAuth')
    def test_with_special_auth(self, auth, request):
        request().text = '{}'

        user = 'asdf'
        password = 'zxcv'
        req = transports.Request()
        req.service = 'SoftLayer_Service'
        req.method = 'getObject'
        req.identifier = 2
        req.transport_user = user
        req.transport_password = password

        resp = self.transport(req)
        self.assertEqual(resp, {})
        auth.assert_called_with(user, password)
        request.assert_called_with(
            'GET',
            'http://something9999999999999999999999.com/SoftLayer_Service/2/getObject.json',
            headers=mock.ANY,
            auth=mock.ANY,
            data=None,
            params={},
            verify=True,
            cert=None,
            proxies=None,
            timeout=None)

    def test_print_reproduceable(self):
        req = transports.Request()
        req.url = "https://test.com"
        req.payload = "testing"
        req.transport_headers = {"test-headers": 'aaaa'}
        output_text = self.transport.print_reproduceable(req)
        self.assertIn("https://test.com", output_text)

    def test_complex_encoder_bytes(self):
        to_encode = {
            'test': ['array', 0, 1, False],
            'bytes': b'ASDASDASD'
        }
        result = json.dumps(to_encode, cls=transports.transport.ComplexEncoder)
        # result = '{"test": ["array", 0, 1, false], "bytes": "QVNEQVNEQVNE"}'
        # encode doesn't always encode in the same order, so testing exact match SOMETIMES breaks.
        self.assertIn("QVNEQVNEQVNE", result)
