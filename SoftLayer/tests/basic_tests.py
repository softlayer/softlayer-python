import SoftLayer
import SoftLayer.API
import SoftLayer.transport
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os
from mock import patch, MagicMock


def get_creds():
    for key in 'SL_USERNAME SL_API_KEY'.split():
        if key not in os.environ:
            raise unittest.SkipTest(
                'SL_USERNAME and SL_API_KEY environmental variables not set')

    return {
        'endpoint': os.environ.get('SL_API_ENDPOINT') or \
            SoftLayer.API_PUBLIC_ENDPOINT,
        'username': os.environ['SL_USERNAME'],
        'api_key': os.environ['SL_API_KEY']
    }


class Inititialization(unittest.TestCase):
    def test_init(self):
        client = SoftLayer.Client('SoftLayer_User_Customer',
            username='doesnotexist', api_key='issurelywrong', timeout=10)

        self.assertEquals(client._service_name,
            'SoftLayer_User_Customer')
        self.assertEquals(client._headers,
            {'authenticate':
                {'username': 'doesnotexist', 'apiKey': 'issurelywrong'}})
        self.assertEquals(client._endpoint_url,
            SoftLayer.API_PUBLIC_ENDPOINT.rstrip('/'))
        self.assertIsInstance(client.transport, 
            SoftLayer.API.SecureProxyTransport)

    def test_init_w_id(self):
        client = SoftLayer.Client('SoftLayer_User_Customer', 1,
            'doesnotexist', 'issurelywrong')

        self.assertEquals(client._headers,
            {'SoftLayer_User_CustomerInitParameters': {'id': 1},
             'authenticate':
                {'username': 'doesnotexist', 'apiKey': 'issurelywrong'}})
        
    @patch.dict('os.environ',
        {'SL_USERNAME': 'test_user', 'SL_API_KEY': 'test_api_key'})
    def test_env(self):
        client = SoftLayer.Client()
        self.assertEquals(client._headers,
            {'authenticate':
                {'username': 'test_user', 'apiKey': 'test_api_key'}})

    @patch('SoftLayer.API.API_USERNAME', 'test_user')
    @patch('SoftLayer.API.API_KEY', 'test_api_key')
    def test_globals(self):
        client = SoftLayer.Client()
        self.assertEquals(client._headers,
            {'authenticate':
                {'username': 'test_user', 'apiKey': 'test_api_key'}})

    @patch('SoftLayer.API.API_USERNAME', None)
    @patch('SoftLayer.API.API_KEY', None)
    @patch.dict('os.environ', {'SL_USERNAME': '', 'SL_API_KEY': ''})
    def test_no_username(self):
        self.assertRaises(SoftLayer.SoftLayerError, SoftLayer.Client)

    def test_non_secure_endpoint(self):
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong',
            endpoint_url="http://example.com")
        self.assertIsInstance(client.transport, 
            SoftLayer.API.ProxyTransport)

    def test_set_raw_header(self):
        client = SoftLayer.Client(
                username='doesnotexist',
                api_key='issurelywrong'
            )
        client.transport = MagicMock()
        client.add_raw_header("RAW", "HEADER")
        client.transport.set_raw_header.assert_called_with("RAW", "HEADER")

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


class Transport(unittest.TestCase):
    def test_exercise_set_raw_headers(self):
        transport = SoftLayer.transport.ProxyTransport()
        transport.set_raw_header('RAW', 'HEADER')

        m = MagicMock()
        transport.send_user_agent(m)
        m.putheader.assert_any_call('RAW', 'HEADER')
        m.putheader.assert_any_call('User-Agent', 'SoftLayer Python 2.0.0')


class APICalls(unittest.TestCase):
    @patch('SoftLayer.API.Client._server_proxy')
    def test_old_api(self, m):
        client = SoftLayer.API.Client(
            'SoftLayer_Account', None, 'doesnotexist', 'issurelywrong')

        return_value = client.METHOD()
        m.return_value.METHOD.assert_called_with({
            'headers': {
                'authenticate': 
                    {'username': 'doesnotexist', 'apiKey': 'issurelywrong'}}})
        self.assertEquals(m.return_value.METHOD(), return_value)

    @patch('SoftLayer.API.Client._server_proxy')
    def test_complex_old_api(self, m):
        client = SoftLayer.API.Client(
            'SoftLayer_Account', None, 'doesnotexist', 'issurelywrong')

        client.set_result_limit(9, offset=10)
        client.set_object_mask({'object': {'attribute': ''}})

        return_value = client['SERVICE'].METHOD(1234,
            id=5678,
            mask={'object': {'attribute': ''}},
            filter={'TYPE': {'obj': {'attribute': '^= prefix'}}},
            limit=9, offset=10)
        m.return_value.METHOD.assert_called_with({
            'headers': {
                'SoftLayer_SERVICEObjectMask': {
                    'mask': {'object': {'attribute': ''}}},
                'SoftLayer_SERVICEObjectFilter': {
                    'TYPE': {
                        'obj': {'attribute': {'operation': '^= prefix'}}}},
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'},
                'SoftLayer_SERVICEInitParameters': {'id': 5678},
                'resultLimit': {'limit': 9, 'offset': 10}}}, 1234)

        self.assertEquals(m.return_value.METHOD(), return_value)

    def test_old_api_no_service(self):
        client = SoftLayer.Client(username='doesnotexist',
            api_key='issurelywrong')
        self.assertRaises(SoftLayer.SoftLayerError, client.METHOD)

    @patch('SoftLayer.API.Client._server_proxy')
    def test_simple_call(self, m):
        client = SoftLayer.Client(username='doesnotexist',
            api_key='issurelywrong')

        return_value = client['SERVICE'].METHOD()
        m.return_value.METHOD.assert_called_with({
            'headers': {
                'authenticate': 
                    {'username': 'doesnotexist', 'apiKey': 'issurelywrong'}}})
        self.assertEquals(m.return_value.METHOD(), return_value)

    @patch('SoftLayer.API.Client._server_proxy')
    def test_complex(self, m):
        client = SoftLayer.Client(username='doesnotexist',
            api_key='issurelywrong')

        return_value = client['SERVICE'].METHOD(1234,
            id=5678,
            mask={'object': {'attribute': ''}},
            filter={'TYPE': {'obj': {'attribute': '^= prefix'}}},
            limit=9, offset=10)
        m.return_value.METHOD.assert_called_with({
            'headers': {
                'SoftLayer_SERVICEObjectMask': {
                    'mask': {'object': {'attribute': ''}}},
                'SoftLayer_SERVICEObjectFilter': {
                    'TYPE': {
                        'obj': {'attribute': {'operation': '^= prefix'}}}},
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'},
                'SoftLayer_SERVICEInitParameters': {'id': 5678},
                'resultLimit': {'limit': 9, 'offset': 10}}}, 1234)

        self.assertEquals(m.return_value.METHOD(), return_value)


class UnauthedUser(unittest.TestCase):
    def test_failed_auth(self):
        client = SoftLayer.Client('SoftLayer_User_Customer', None,
            'doesnotexist', 'issurelywrong', timeout=20)
        self.assertRaises(SoftLayer.SoftLayerError,
            client.getPortalLoginToken)


class AuthedUser(unittest.TestCase):
    def test_dns(self):
        creds = get_creds()
        client = SoftLayer.Client(
            username=creds['username'],
            api_key=creds['api_key'],
            endpoint_url=creds['endpoint'],
            timeout=20)
        client["SoftLayer_Dns_Domain"].getByDomainName('p.sftlyr.ws')

    def test_result_types(self):
        creds = get_creds()
        client = SoftLayer.Client('SoftLayer_User_Security_Question',
            username=creds['username'],
            api_key=creds['api_key'],
            endpoint_url=creds['endpoint'],
            timeout=20)
        result = client.getAllObjects()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIsInstance(result[0]['viewable'], int)
        self.assertIsInstance(result[0]['question'], str)
        self.assertIsInstance(result[0]['id'], int)
        self.assertIsInstance(result[0]['displayOrder'], int)

