import SoftLayer
import SoftLayer.API
from SoftLayer.consts import USER_AGENT
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os
from mock import patch, MagicMock


class Inititialization(unittest.TestCase):
    def test_init(self):
        client = SoftLayer.Client('SoftLayer_User_Customer',
                                  username='doesnotexist',
                                  api_key='issurelywrong', timeout=10)

        self.assertEquals(client._service_name,
                          'SoftLayer_User_Customer')
        self.assertEquals(client._headers, {
            'authenticate': {
                'username': 'doesnotexist',
                'apiKey': 'issurelywrong'
            }
        })
        self.assertEquals(client._endpoint_url,
                          SoftLayer.API_PUBLIC_ENDPOINT.rstrip('/'))

    def test_init_w_id(self):
        client = SoftLayer.Client('SoftLayer_User_Customer', 1,
                                  'doesnotexist', 'issurelywrong')

        self.assertEquals(client._headers, {
            'SoftLayer_User_CustomerInitParameters': {'id': 1},
            'authenticate': {
                'username': 'doesnotexist', 'apiKey': 'issurelywrong'}})

    @patch.dict('os.environ', {
        'SL_USERNAME': 'test_user', 'SL_API_KEY': 'test_api_key'})
    def test_env(self):
        client = SoftLayer.Client()
        self.assertEquals(client._headers, {
            'authenticate': {
                'username': 'test_user', 'apiKey': 'test_api_key'}})

    @patch('SoftLayer.API.API_USERNAME', 'test_user')
    @patch('SoftLayer.API.API_KEY', 'test_api_key')
    def test_globals(self):
        client = SoftLayer.Client()
        self.assertEquals(client._headers, {
            'authenticate': {
                'username': 'test_user', 'apiKey': 'test_api_key'}})

    @patch('SoftLayer.API.API_USERNAME', None)
    @patch('SoftLayer.API.API_KEY', None)
    @patch.dict('os.environ', {'SL_USERNAME': '', 'SL_API_KEY': ''})
    def test_no_username(self):
        self.assertRaises(SoftLayer.SoftLayerError, SoftLayer.Client)


class ClientMethods(unittest.TestCase):
    def test_help(self):
        help(SoftLayer)
        help(SoftLayer.Client)
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        help(client)
        help(client['SERVICE'])

    def test_set_raw_header_old(self):
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        client.transport = MagicMock()
        client.add_raw_header("RAW", "HEADER")
        self.assertEquals(client._raw_headers, {'RAW': 'HEADER'})

    def test_add_header_invalid(self):
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        client.transport = MagicMock()
        self.assertRaises(SoftLayer.SoftLayerError,
                          client.add_header, "", "HEADER")

    def test_remove_header(self):
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        client.remove_header("authenticate")
        self.assertNotIn("authenticate", client._headers)

    def test_repr(self):
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        self.assertIn("Client", repr(client))

    def test_service_repr(self):
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        self.assertIn("Service", repr(client['SERVICE']))


class APICalls(unittest.TestCase):
    @patch('SoftLayer.API.make_api_call')
    def test_old_api(self, make_api_call):
        client = SoftLayer.API.Client(
            'SoftLayer_SERVICE', None, 'doesnotexist', 'issurelywrong',
            endpoint_url="ENDPOINT")

        return_value = client.METHOD()
        make_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (),
            headers={
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'}},
            verbose=False,
            timeout=None,
            http_headers={
                'Content-Type': 'application/xml',
                'User-Agent': USER_AGENT,
            })

    @patch('SoftLayer.API.make_api_call')
    def test_complex_old_api(self, make_api_call):
        client = SoftLayer.API.Client(
            'SoftLayer_SERVICE', None, 'doesnotexist', 'issurelywrong',
            endpoint_url="ENDPOINT")

        client.set_result_limit(9, offset=10)
        client.set_object_mask({'object': {'attribute': ''}})
        client.add_raw_header("RAW", "HEADER")

        return_value = client.METHOD(
            1234,
            id=5678,
            mask={'object': {'attribute': ''}},
            filter={'TYPE': {'obj': {'attribute': '^= prefix'}}},
            limit=9, offset=10)

        make_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (1234, ),
            headers={
                'SoftLayer_SERVICEObjectMask': {
                    'mask': {'object': {'attribute': ''}}},
                'SoftLayer_SERVICEObjectFilter': {
                    'TYPE': {
                        'obj': {'attribute': {'operation': '^= prefix'}}}},
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'},
                'SoftLayer_SERVICEInitParameters': {'id': 5678},
                'resultLimit': {'limit': 9, 'offset': 10}},
            verbose=False,
            timeout=None,
            http_headers={
                'RAW': 'HEADER',
                'Content-Type': 'application/xml',
                'User-Agent': USER_AGENT,
            })

    def test_old_api_no_service(self):
        client = SoftLayer.Client(username='doesnotexist',
                                  api_key='issurelywrong')
        self.assertRaises(SoftLayer.SoftLayerError, client.METHOD)

    @patch('SoftLayer.API.make_api_call')
    def test_simple_call(self, make_api_call):
        client = SoftLayer.Client(
            username='doesnotexist', api_key='issurelywrong',
            endpoint_url="ENDPOINT")

        return_value = client['SERVICE'].METHOD()
        make_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (),
            headers={
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'}},
            verbose=False,
            timeout=None,
            http_headers={
                'Content-Type': 'application/xml',
                'User-Agent': USER_AGENT,
            })

    @patch('SoftLayer.API.make_api_call')
    def test_complex(self, make_api_call):
        client = SoftLayer.Client(username='doesnotexist',
                                  api_key='issurelywrong',
                                  endpoint_url="ENDPOINT")

        return_value = client['SERVICE'].METHOD(
            1234,
            id=5678,
            mask={'object': {'attribute': ''}},
            raw_headers={'RAW': 'HEADER'},
            filter={'TYPE': {'obj': {'attribute': '^= prefix'}}},
            limit=9, offset=10)

        make_api_call.assert_called_with(
            'ENDPOINT/SoftLayer_SERVICE', 'METHOD', (1234, ),
            headers={
                'SoftLayer_SERVICEObjectMask': {
                    'mask': {'object': {'attribute': ''}}},
                'SoftLayer_SERVICEObjectFilter': {
                    'TYPE': {
                        'obj': {'attribute': {'operation': '^= prefix'}}}},
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'},
                'SoftLayer_SERVICEInitParameters': {'id': 5678},
                'resultLimit': {'limit': 9, 'offset': 10}},
            verbose=False,
            timeout=None,
            http_headers={
                'RAW': 'HEADER',
                'Content-Type': 'application/xml',
                'User-Agent': USER_AGENT,
            })
