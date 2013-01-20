import SoftLayer
import SoftLayer.API
import xmlrpclib
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os
from mock import patch, MagicMock


NO_CREDS_TEXT = 'SL_USERNAME and SL_API_KEY environmental variables not set'
HAS_CREDS = True
for key in 'SL_USERNAME SL_API_KEY'.split():
    if key not in os.environ:
        HAS_CREDS = False
        break

def get_creds():
    return {
        'endpoint': os.environ['SL_API_ENDPOINT'] or \
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
        
    def test_env(self):
        with patch.dict('os.environ', 
            {'SL_USERNAME': 'test_user', 'SL_API_KEY': 'test_api_key'}):
            client = SoftLayer.Client('SoftLayer_User_Customer')
            self.assertEquals(client._headers,
                {'authenticate':
                    {'username': 'test_user', 'apiKey': 'test_api_key'}})

    @patch('SoftLayer.API.API_USERNAME', 'test_user')
    @patch('SoftLayer.API.API_KEY', 'test_api_key')
    def test_globals(self):
        client = SoftLayer.Client('SoftLayer_User_Customer')
        self.assertEquals(client._headers,
            {'authenticate':
                {'username': 'test_user', 'apiKey': 'test_api_key'}})


class APICalls(unittest.TestCase):
    @patch('xmlrpclib.ServerProxy')
    def test_old_api(self, m):
        client = SoftLayer.API.Client(
            'SoftLayer_Account', None, 'doesnotexist', 'issurelywrong')

        return_value = client.METHOD()
        m.return_value.METHOD.assert_called_with({
            'headers': {
                'authenticate': 
                    {'username': 'doesnotexist', 'apiKey': 'issurelywrong'}}})
        self.assertEquals(m.return_value.METHOD(), return_value)

    @patch('xmlrpclib.ServerProxy')
    def test_complex_old_api(self, m):
        client = SoftLayer.API.Client(
            'SoftLayer_Account', None, 'doesnotexist', 'issurelywrong')

        client.set_result_limit(9, offset=10)
        client.set_object_mask({'object': {'attribute': ''}})

        return_value = client['SERVICE'].METHOD(1234,
            mask={'object': {'attribute': ''}},
            filter={'TYPE.obj.attribute': '^= prefix'}, limit=9, offset=10)
        m.return_value.METHOD.assert_called_with({
            'headers': {
                'SoftLayer_SERVICEObjectMask': {
                    'mask': {'object': {'attribute': ''}}},
                'SoftLayer_SERVICEObjectFilter': {
                    'TYPE': {
                        'obj': {'attribute': {'operation': '^= prefix'}}}},
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'},
                'resultLimit': {'limit': 9, 'offset': 10}}}, 1234)

        self.assertEquals(m.return_value.METHOD(), return_value)

    @patch('xmlrpclib.ServerProxy')
    def test_simple_call(self, m):
        client = SoftLayer.Client(username='doesnotexist',
            api_key='issurelywrong')

        return_value = client['SERVICE'].METHOD()
        m.return_value.METHOD.assert_called_with({
            'headers': {
                'authenticate': 
                    {'username': 'doesnotexist', 'apiKey': 'issurelywrong'}}})
        self.assertEquals(m.return_value.METHOD(), return_value)

    @patch('xmlrpclib.ServerProxy')
    def test_complex(self, m):
        client = SoftLayer.Client(username='doesnotexist',
            api_key='issurelywrong')

        return_value = client['SERVICE'].METHOD(1234,
            mask={'object': {'attribute': ''}},
            filter={'TYPE.obj.attribute': '^= prefix'}, limit=9, offset=10)
        m.return_value.METHOD.assert_called_with({
            'headers': {
                'SoftLayer_SERVICEObjectMask': {
                    'mask': {'object': {'attribute': ''}}},
                'SoftLayer_SERVICEObjectFilter': {
                    'TYPE': {
                        'obj': {'attribute': {'operation': '^= prefix'}}}},
                'authenticate': {
                    'username': 'doesnotexist', 'apiKey': 'issurelywrong'},
                'resultLimit': {'limit': 9, 'offset': 10}}}, 1234)

        self.assertEquals(m.return_value.METHOD(), return_value)


class UnauthedUser(unittest.TestCase):
    def test_failed_auth(self):
        client = SoftLayer.Client('SoftLayer_User_Customer', None,
            'doesnotexist', 'issurelywrong', timeout=20)
        self.assertRaises(SoftLayer.SoftLayerError,
            client.getPortalLoginToken)


@unittest.skipIf(not HAS_CREDS, NO_CREDS_TEXT)
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
