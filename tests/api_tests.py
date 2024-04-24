"""
    SoftLayer.tests.api_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import io
import os
from unittest import mock as mock
import requests

import SoftLayer
import SoftLayer.API
from SoftLayer import testing
from SoftLayer import transports
from SoftLayer import exceptions
from SoftLayer import auth as slauth


class Initialization(testing.TestCase):
    def test_init(self):
        client = SoftLayer.Client(username='doesnotexist',
                                  api_key='issurelywrong',
                                  timeout=10,
                                  endpoint_url='http://example.com/v3/xmlrpc/')

        self.assertIsInstance(client.auth, SoftLayer.BasicAuthentication)
        self.assertEqual(client.auth.username, 'doesnotexist')
        self.assertEqual(client.auth.api_key, 'issurelywrong')
        self.assertIsNotNone(client.transport)
        self.assertIsInstance(client.transport, transports.XmlRpcTransport)
        self.assertEqual(client.transport.timeout, 10)

    def test_init_with_rest_url(self):
        client = SoftLayer.Client(username='doesnotexist',
                                  api_key='issurelywrong',
                                  timeout=10,
                                  endpoint_url='http://example.com/v3/rest/')

        self.assertIsInstance(client.auth, SoftLayer.BasicHTTPAuthentication)
        self.assertEqual(client.auth.username, 'doesnotexist')
        self.assertEqual(client.auth.api_key, 'issurelywrong')
        self.assertIsNotNone(client.transport)
        self.assertIsInstance(client.transport, transports.RestTransport)
        self.assertEqual(client.transport.endpoint_url,
                         'http://example.com/v3/rest')
        self.assertEqual(client.transport.timeout, 10)

    @mock.patch('SoftLayer.config.get_client_settings')
    def test_env(self, get_client_settings):
        auth = mock.Mock()
        get_client_settings.return_value = {
            'timeout': 10,
            'endpoint_url': 'http://endpoint_url/',
        }
        client = SoftLayer.Client(auth=auth)
        self.assertEqual(client.auth.get_headers(), auth.get_headers())
        self.assertEqual(client.transport.timeout, 10)
        self.assertEqual(client.transport.endpoint_url, 'http://endpoint_url')


class ClientMethods(testing.TestCase):

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

    def test_len(self):
        client = SoftLayer.Client(
            username='doesnotexist',
            api_key='issurelywrong'
        )
        self.assertEqual(len(client), 0)


class APIClient(testing.TestCase):

    def test_simple_call(self):
        mock = self.set_mock('SoftLayer_SERVICE', 'METHOD')
        mock.return_value = {"test": "result"}

        resp = self.client['SERVICE'].METHOD()

        self.assertEqual(resp, {"test": "result"})
        self.assert_called_with('SoftLayer_SERVICE', 'METHOD',
                                mask=None,
                                filter=None,
                                identifier=None,
                                args=tuple(),
                                limit=None,
                                offset=None,
                                )

    def test_simple_call_2(self):
        mock = self.set_mock('SoftLayer_SERVICE', 'METHOD')
        mock.return_value = {"test": "result"}

        resp = self.client.call('SERVICE', 'METHOD', {'networkComponents': [{'maxSpeed': 100}]})

        self.assertEqual(resp, {"test": "result"})
        self.assert_called_with('SoftLayer_SERVICE', 'METHOD',
                                mask=None, filter=None, identifier=None,
                                args=({'networkComponents': [{'maxSpeed': 100}]},), limit=None, offset=None,
                                )

    def test_verify_request_false(self):
        client = SoftLayer.BaseClient(transport=self.mocks)
        mock = self.set_mock('SoftLayer_SERVICE', 'METHOD')
        mock.return_value = {"test": "result"}

        resp = client.call('SERVICE', 'METHOD', verify=False)

        self.assertEqual(resp, {"test": "result"})
        self.assert_called_with('SoftLayer_SERVICE', 'METHOD', verify=False)

    def test_verify_request_true(self):
        client = SoftLayer.BaseClient(transport=self.mocks)
        mock = self.set_mock('SoftLayer_SERVICE', 'METHOD')
        mock.return_value = {"test": "result"}

        resp = client.call('SERVICE', 'METHOD', verify=True)

        self.assertEqual(resp, {"test": "result"})
        self.assert_called_with('SoftLayer_SERVICE', 'METHOD', verify=True)

    def test_verify_request_not_specified(self):
        client = SoftLayer.BaseClient(transport=self.mocks)
        mock = self.set_mock('SoftLayer_SERVICE', 'METHOD')
        mock.return_value = {"test": "result"}

        resp = client.call('SERVICE', 'METHOD')

        self.assertEqual(resp, {"test": "result"})
        self.assert_called_with('SoftLayer_SERVICE', 'METHOD', verify=None)

    @mock.patch('SoftLayer.API.BaseClient.iter_call')
    def test_iterate(self, _iter_call):
        self.client['SERVICE'].METHOD(iter=True)
        _iter_call.assert_called_with('SERVICE', 'METHOD')

    @mock.patch('SoftLayer.API.BaseClient.iter_call')
    def test_service_iter_call(self, _iter_call):
        self.client['SERVICE'].iter_call('METHOD', 'ARG')
        _iter_call.assert_called_with('SERVICE', 'METHOD', 'ARG')

    @mock.patch('SoftLayer.API.BaseClient.iter_call')
    def test_service_iter_call_with_chunk(self, _iter_call):
        self.client['SERVICE'].iter_call('METHOD', 'ARG', chunk=2)
        _iter_call.assert_called_with('SERVICE', 'METHOD', 'ARG', chunk=2)

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_iter_call(self, _call):
        # chunk=100, no limit
        _call.side_effect = [
            transports.SoftLayerListResult(range(100), 125),
            transports.SoftLayerListResult(range(100, 125), 125)
        ]
        result = list(self.client.iter_call('SERVICE', 'METHOD', iter=True))

        self.assertEqual(list(range(125)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=0),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=100),
        ])
        _call.reset_mock()

        # chunk=100, no limit. Requires one extra request.
        _call.side_effect = [
            transports.SoftLayerListResult(range(100), 201),
            transports.SoftLayerListResult(range(100, 200), 201),
            transports.SoftLayerListResult([], 201)
        ]
        result = list(self.client.iter_call('SERVICE', 'METHOD', iter=True))
        self.assertEqual(list(range(200)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=0),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=100),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=200),
        ])
        _call.reset_mock()

        # chunk=25, limit=30
        _call.side_effect = [
            transports.SoftLayerListResult(range(0, 25), 30),
            transports.SoftLayerListResult(range(25, 30), 30)
        ]
        result = list(self.client.iter_call(
            'SERVICE', 'METHOD', iter=True, limit=25))
        self.assertEqual(list(range(30)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', iter=False, limit=25, offset=0),
            mock.call('SERVICE', 'METHOD', iter=False, limit=25, offset=25),
        ])
        _call.reset_mock()

        # A non-list was returned
        _call.side_effect = ["test"]
        result = list(self.client.iter_call('SERVICE', 'METHOD', iter=True))
        self.assertEqual(["test"], result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', iter=False, limit=100, offset=0),
        ])
        _call.reset_mock()

        _call.side_effect = [
            transports.SoftLayerListResult(range(0, 25), 30),
            transports.SoftLayerListResult(range(25, 30), 30)
        ]
        result = list(self.client.iter_call('SERVICE', 'METHOD', 'ARG',
                                            iter=True,
                                            limit=25,
                                            offset=12))
        self.assertEqual(list(range(30)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', 'ARG',
                      iter=False, limit=25, offset=12),
            mock.call('SERVICE', 'METHOD', 'ARG',
                      iter=False, limit=25, offset=37),
        ])

        # Chunk size of 0 is invalid
        self.assertRaises(
            AttributeError,
            lambda: list(self.client.iter_call('SERVICE', 'METHOD',
                                               iter=True, limit=0)))

    def test_call_invalid_arguments(self):
        self.assertRaises(
            TypeError,
            self.client.call, 'SERVICE', 'METHOD', invalid_kwarg='invalid')

    def test_call_compression_disabled(self):
        mocked = self.set_mock('SoftLayer_SERVICE', 'METHOD')
        mocked.return_value = {}

        self.client['SERVICE'].METHOD(compress=False)

        calls = self.calls('SoftLayer_SERVICE', 'METHOD')
        self.assertEqual(len(calls), 1)
        headers = calls[0].transport_headers
        self.assertEqual(headers.get('accept-encoding'), 'identity')

    def test_call_compression_enabled(self):
        mocked = self.set_mock('SoftLayer_SERVICE', 'METHOD')
        mocked.return_value = {}

        self.client['SERVICE'].METHOD(compress=True)

        calls = self.calls('SoftLayer_SERVICE', 'METHOD')
        self.assertEqual(len(calls), 1)
        headers = calls[0].transport_headers
        self.assertEqual(headers.get('accept-encoding'),
                         'gzip, deflate, compress')

    def test_call_compression_override(self):
        # raw_headers should override compress=False
        mocked = self.set_mock('SoftLayer_SERVICE', 'METHOD')
        mocked.return_value = {}

        self.client['SERVICE'].METHOD(
            compress=False,
            raw_headers={'Accept-Encoding': 'gzip'})

        calls = self.calls('SoftLayer_SERVICE', 'METHOD')
        self.assertEqual(len(calls), 1)
        headers = calls[0].transport_headers
        self.assertEqual(headers.get('accept-encoding'), 'gzip')

    def test_special_services(self):
        # Tests for the special classes that don't need to start with SoftLayer_
        self.client.call('BluePages_Search', 'findBluePagesProfile')
        self.assert_called_with('BluePages_Search', 'findBluePagesProfile')


class UnauthenticatedAPIClient(testing.TestCase):
    def set_up(self):
        self.client = SoftLayer.Client(endpoint_url="ENDPOINT")

    @mock.patch('SoftLayer.config.get_client_settings')
    def test_init(self, get_client_settings):
        get_client_settings.return_value = {}
        client = SoftLayer.Client()
        self.assertIsNone(client.auth)

    @mock.patch('SoftLayer.config.get_client_settings')
    def test_init_with_proxy(self, get_client_settings):
        get_client_settings.return_value = {'proxy': 'http://localhost:3128'}
        client = SoftLayer.Client()
        self.assertEqual(client.transport.proxy, 'http://localhost:3128')

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_authenticate_with_password(self, _call):
        _call.return_value = {
            'userId': 12345,
            'hash': 'TOKEN',
        }
        self.client.authenticate_with_password('USERNAME', 'PASSWORD')
        _call.assert_called_with(
            'User_Customer',
            'getPortalLoginToken',
            'USERNAME',
            'PASSWORD',
            None,
            None)
        self.assertIsNotNone(self.client.auth)
        self.assertEqual(self.client.auth.user_id, 12345)
        self.assertEqual(self.client.auth.auth_token, 'TOKEN')


class EmployeeClientTests(testing.TestCase):


    @staticmethod
    def setup_response(filename, status_code=200, total_items=1):
        basepath = os.path.dirname(__file__)
        body = b''
        with open(f"{basepath}/../SoftLayer/fixtures/xmlrpc/{filename}.xml", 'rb') as fixture:
            body = fixture.read()
        response = requests.Response()
        list_body = body
        response.raw = io.BytesIO(list_body)
        response.headers['SoftLayer-Total-Items'] = total_items
        response.status_code = status_code
        return response


    def set_up(self):
        self.client = SoftLayer.API.EmployeeClient(config_file='./tests/testconfig')

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_auth_with_pass_failure(self, api_response):
        api_response.return_value = self.setup_response('invalidLogin')
        exception = self.assertRaises(
            exceptions.SoftLayerAPIError,
            self.client.authenticate_with_password, 'testUser', 'testPassword', '123456')
        self.assertEqual(exception.faultCode, "SoftLayer_Exception_Public")

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_auth_with_pass_success(self, api_response):
        api_response.return_value = self.setup_response('successLogin')
        result = self.client.authenticate_with_password('testUser', 'testPassword', '123456')
        print(result)
        self.assertEqual(result['userId'], 1234)
        self.assertEqual(self.client.settings['softlayer']['userid'], '1234')
        self.assertIn('x'*200, self.client.settings['softlayer']['access_token'])

    def test_auth_with_hash(self):
        self.client.auth = None
        self.client.authenticate_with_hash(5555, 'abcdefg')
        self.assertEqual(self.client.auth.user_id, 5555)
        self.assertEqual(self.client.auth.hash, 'abcdefg')

    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_refresh_token(self, api_response):
        api_response.return_value = self.setup_response('refreshSuccess')
        result = self.client.refresh_token(9999, 'qweasdzxcqweasdzxcqweasdzxc')
        self.assertEqual(self.client.auth.user_id, 9999)
        self.assertIn('REFRESHEDTOKENaaaa', self.client.auth.hash)
    
    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_expired_token_is_refreshed(self, api_response):
        api_response.side_effect = [
            self.setup_response('expiredToken'),
            self.setup_response('refreshSuccess'),
            self.setup_response('Employee_getObject')
        ]
        self.client.auth = slauth.EmployeeAuthentication(5555, 'aabbccee')
        self.client.settings['softlayer']['userid'] = '5555'
        result = self.client.call('SoftLayer_User_Employee', 'getObject', id=5555)
        self.assertIn('REFRESHEDTOKENaaaa', self.client.auth.hash)
        self.assertEqual('testUser', result['username'])
        
    @mock.patch('SoftLayer.transports.xmlrpc.requests.Session.request')
    def test_expired_token_is_really_expored(self, api_response):
        api_response.side_effect = [
            self.setup_response('expiredToken'),
            self.setup_response('expiredToken')
        ]
        self.client.auth = slauth.EmployeeAuthentication(5555, 'aabbccee')
        self.client.settings['softlayer']['userid'] = '5555'
        exception = self.assertRaises(
            exceptions.SoftLayerAPIError,
            self.client.call, 'SoftLayer_User_Employee', 'getObject', id=5555)
        self.assertEqual(None, self.client.auth)
        self.assertEqual(exception.faultCode, "SoftLayer_Exception_EncryptedToken_Expired")

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_account_check(self, _call):
        self.client.transport = self.mocks
        exception = self.assertRaises(
            exceptions.SoftLayerError,
            self.client.call, "SoftLayer_Account", "getObject")
        self.assertEqual(str(exception), "SoftLayer_Account service requires an ID")
        self.client.account_id = 1234
        self.client.call("SoftLayer_Account", "getObject")
        self.client.call("SoftLayer_Account", "getObject1", id=9999)

        _call.assert_has_calls([
            mock.call(self.client, 'SoftLayer_Account', 'getObject', id=1234),
            mock.call(self.client, 'SoftLayer_Account', 'getObject1', id=9999),
        ])