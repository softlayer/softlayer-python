try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
from mock import patch, MagicMock

from SoftLayer import SoftLayerAPIError, TransportError
from SoftLayer.transport import make_rest_api_call
from requests import HTTPError, RequestException


class TestRestAPICall(unittest.TestCase):

    @patch('SoftLayer.transport.requests.request')
    def test_json(self, request):
        request().content = '{}'
        resp = make_rest_api_call('GET', 'http://something.com/path/to/resourse.json')
        self.assertEqual(resp, {})
        request.assert_called_with(
            'GET', 'http://something.com/path/to/resourse.json',
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
            'http://something.com/path/to/resourse.json')

    @patch('SoftLayer.transport.requests.request')
    def test_text(self, request):
        request().text = 'content'
        resp = make_rest_api_call('GET', 'http://something.com/path/to/resourse.txt')
        self.assertEqual(resp, 'content')
        request.assert_called_with(
            'GET', 'http://something.com/path/to/resourse.txt',
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
            'http://something.com/path/to/resourse.txt')

    @patch('SoftLayer.transport.requests.request')
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
            'http://something.com/path/to/resourse.txt')
