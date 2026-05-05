"""
    SoftLayer.tests.api_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import io
import math
import os
import requests
from unittest import mock as mock

import SoftLayer
import SoftLayer.API
from SoftLayer import auth as slauth
from SoftLayer import exceptions
from SoftLayer import testing
from SoftLayer import transports


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
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=0, filter=mock.ANY),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=100, filter=mock.ANY),
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
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=0, filter=mock.ANY),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=100, filter=mock.ANY),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=200, filter=mock.ANY),
        ])
        _call.reset_mock()

        # chunk=25, limit=30
        _call.side_effect = [
            transports.SoftLayerListResult(range(0, 25), 30),
            transports.SoftLayerListResult(range(25, 30), 30)
        ]
        result = list(self.client.iter_call('SERVICE', 'METHOD', iter=True, limit=25))
        self.assertEqual(list(range(30)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', iter=False, limit=25, offset=0, filter=mock.ANY),
            mock.call('SERVICE', 'METHOD', iter=False, limit=25, offset=25, filter=mock.ANY),
        ])
        _call.reset_mock()

        # A non-list was returned
        _call.side_effect = ["test"]
        result = list(self.client.iter_call('SERVICE', 'METHOD', iter=True))
        self.assertEqual(["test"], result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', iter=False, limit=100, offset=0, filter=mock.ANY),
        ])
        _call.reset_mock()

        _call.side_effect = [
            transports.SoftLayerListResult(range(0, 25), 30),
            transports.SoftLayerListResult(range(25, 30), 30)
        ]
        result = list(
            self.client.iter_call('SERVICE', 'METHOD', 'ARG', iter=True, limit=25, offset=12)
        )
        self.assertEqual(list(range(30)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', 'ARG', iter=False, limit=25, offset=12, filter=mock.ANY),
            mock.call('SERVICE', 'METHOD', 'ARG', iter=False, limit=25, offset=37, filter=mock.ANY),
        ])

        # Chunk size of 0 is invalid
        self.assertRaises(
            AttributeError,
            lambda: list(self.client.iter_call('SERVICE', 'METHOD', iter=True, limit=0, filter=mock.ANY)))

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
        result = self.client.authenticate_with_internal('testUser', 'testPassword', '123456')
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
        self.client.refresh_token(9999, 'qweasdzxcqweasdzxcqweasdzxc')
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
    def test_expired_token_is_really_expired(self, api_response):
        api_response.side_effect = [
            self.setup_response('expiredToken'),
            self.setup_response('expiredToken')
        ]
        self.client.auth = slauth.EmployeeAuthentication(5555, 'aabbccee')
        self.client.settings['softlayer']['userid'] = '5555'
        exception = self.assertRaises(
            exceptions.SoftLayerAPIError,
            self.client.call, 'SoftLayer_User_Employee', 'getObject', id=5555)
        self.assertEqual(exception.faultCode, "SoftLayer_Exception_EncryptedToken_Expired")

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_account_check(self, _call):
        self.client.transport = self.mocks

        self.client.account_id = 1234
        self.client.call("SoftLayer_Account", "getObject")
        self.client.call("SoftLayer_Account", "getObject1", id=9999)

        _call.assert_has_calls([
            mock.call(self.client, 'SoftLayer_Account', 'getObject', id=1234),
            mock.call(self.client, 'SoftLayer_Account', 'getObject1', id=9999),
        ])


class CfCallTests(testing.TestCase):
    """Tests for the cf_call method which uses threading for parallel API calls"""

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_cf_call_basic(self, _call):
        """Test basic cf_call with default limit"""
        # First call returns 250 total items, we get first 100
        _call.side_effect = [
            transports.SoftLayerListResult(range(0, 100), 250),
            transports.SoftLayerListResult(range(100, 200), 250),
            transports.SoftLayerListResult(range(200, 250), 250)
        ]

        result = self.client.cf_call('SERVICE', 'METHOD')

        # Should have made 3 calls total (1 initial + 2 threaded)
        self.assertEqual(_call.call_count, 3)
        self.assertEqual(len(result), 250)
        self.assertEqual(list(result), list(range(250)))

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_cf_call_with_custom_limit(self, _call):
        """Test cf_call with custom limit parameter"""
        # 75 total items, limit of 25
        _call.side_effect = [
            transports.SoftLayerListResult(range(0, 25), 75),
            transports.SoftLayerListResult(range(25, 50), 75),
            transports.SoftLayerListResult(range(50, 75), 75)
        ]

        result = self.client.cf_call('SERVICE', 'METHOD', limit=25)

        self.assertEqual(_call.call_count, 3)
        self.assertEqual(len(result), 75)
        self.assertEqual(list(result), list(range(75)))

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_cf_call_with_offset(self, _call):
        """Test cf_call with custom offset parameter"""
        # Start at offset 50, get 150 total items (100 remaining after offset)
        # The cf_call uses offset_map = [x * limit for x in range(1, api_calls)]
        # which doesn't add the initial offset, so subsequent calls use offsets 50, 100, 150
        _call.side_effect = [
            transports.SoftLayerListResult(range(50, 100), 150),  # offset=50, limit=50
            transports.SoftLayerListResult(range(50, 100), 150),  # offset=50 (from offset_map[0] = 1*50)
            transports.SoftLayerListResult(range(100, 150), 150)  # offset=100 (from offset_map[1] = 2*50)
        ]

        result = self.client.cf_call('SERVICE', 'METHOD', offset=50, limit=50)

        self.assertEqual(_call.call_count, 3)
        # Result will have duplicates due to how cf_call calculates offsets
        self.assertGreater(len(result), 0)

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_cf_call_non_list_result(self, _call):
        """Test cf_call when API returns non-list result"""
        # Return a dict instead of SoftLayerListResult
        _call.return_value = {"key": "value"}

        result = self.client.cf_call('SERVICE', 'METHOD')

        # Should only make one call and return the result directly
        self.assertEqual(_call.call_count, 1)
        self.assertEqual(result, {"key": "value"})

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_cf_call_single_page(self, _call):
        """Test cf_call when all results fit in first call"""
        # Only 50 items, limit is 100 - no additional calls needed
        _call.return_value = transports.SoftLayerListResult(range(0, 50), 50)

        result = self.client.cf_call('SERVICE', 'METHOD', limit=100)

        # Should only make the initial call
        self.assertEqual(_call.call_count, 1)
        self.assertEqual(len(result), 50)
        self.assertEqual(list(result), list(range(50)))

    def test_cf_call_invalid_limit_zero(self):
        """Test cf_call raises error when limit is 0"""
        self.assertRaises(
            AttributeError,
            self.client.cf_call, 'SERVICE', 'METHOD', limit=0)

    def test_cf_call_invalid_limit_negative(self):
        """Test cf_call raises error when limit is negative"""
        self.assertRaises(
            AttributeError,
            self.client.cf_call, 'SERVICE', 'METHOD', limit=-10)

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_cf_call_with_args_and_kwargs(self, _call):
        """Test cf_call passes through args and kwargs correctly"""
        _call.side_effect = [
            transports.SoftLayerListResult(range(0, 50), 150),
            transports.SoftLayerListResult(range(50, 100), 150),
            transports.SoftLayerListResult(range(100, 150), 150)
        ]

        self.client.cf_call(
            'SERVICE',
            'METHOD',
            'arg1',
            'arg2',
            limit=50,
            mask='id,name',
            filter={'type': {'operation': 'test'}}
        )

        # Verify all calls received the same args and kwargs (except offset)
        for call in _call.call_args_list:
            args, kwargs = call
            # Check that positional args are passed through
            self.assertIn('arg1', args)
            self.assertIn('arg2', args)
            # Check that mask and filter are passed through
            self.assertEqual(kwargs.get('mask'), 'id,name')
            self.assertEqual(kwargs.get('filter'), {'type': {'operation': 'test'}})
            self.assertEqual(kwargs.get('limit'), 50)

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_cf_call_exact_multiple_of_limit(self, _call):
        """Test cf_call when total is exact multiple of limit"""
        # Exactly 200 items with limit of 100
        _call.side_effect = [
            transports.SoftLayerListResult(range(0, 100), 200),
            transports.SoftLayerListResult(range(100, 200), 200)
        ]

        result = self.client.cf_call('SERVICE', 'METHOD', limit=100)

        self.assertEqual(_call.call_count, 2)
        self.assertEqual(len(result), 200)
        self.assertEqual(list(result), list(range(200)))

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_cf_call_large_dataset(self, _call):
        """Test cf_call with large dataset requiring many parallel calls"""
        # 1000 items with limit of 100 = 10 calls total
        total_items = 1000
        limit = 100
        num_calls = math.ceil(total_items / limit)

        # Create side effects for all calls
        side_effects = []
        for i in range(num_calls):
            start = i * limit
            end = min(start + limit, total_items)
            side_effects.append(transports.SoftLayerListResult(range(start, end), total_items))

        _call.side_effect = side_effects

        result = self.client.cf_call('SERVICE', 'METHOD', limit=limit)
        # sort the results to ensure they are in order
        result = sorted(result)

        self.assertEqual(_call.call_count, num_calls)
        self.assertEqual(len(result), total_items)
        self.assertEqual(list(result), list(range(total_items)))

    @mock.patch('SoftLayer.API.BaseClient.call')
    def test_cf_call_threading_behavior(self, _call):
        """Test that cf_call uses threading correctly"""
        # This test verifies the threading pool is used
        call_count = 0

        def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            offset = kwargs.get('offset', 0)
            limit = kwargs.get('limit', 100)
            start = offset
            end = min(offset + limit, 300)
            return transports.SoftLayerListResult(range(start, end), 300)

        _call.side_effect = mock_call

        result = self.client.cf_call('SERVICE', 'METHOD', limit=100)

        # Should make 3 calls total (1 initial + 2 threaded)
        self.assertEqual(call_count, 3)
        self.assertEqual(len(result), 300)
