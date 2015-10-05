"""
    SoftLayer.tests.api_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
import SoftLayer.API
from SoftLayer import testing
from SoftLayer import transports


class Inititialization(testing.TestCase):
    def test_init(self):
        client = SoftLayer.Client(username='doesnotexist',
                                  api_key='issurelywrong',
                                  timeout=10)

        self.assertIsInstance(client.auth, SoftLayer.BasicAuthentication)
        self.assertEqual(client.auth.username, 'doesnotexist')
        self.assertEqual(client.auth.api_key, 'issurelywrong')
        self.assertIsNotNone(client.transport)
        self.assertIsInstance(client.transport, transports.XmlRpcTransport)
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

    def test_complex(self):
        mock = self.set_mock('SoftLayer_SERVICE', 'METHOD')
        mock.return_value = {"test": "result"}
        _filter = {'TYPE': {'attribute': {'operation': '^= prefix'}}}

        resp = self.client['SERVICE'].METHOD(
            1234,
            id=5678,
            mask={'object': {'attribute': ''}},
            headers={'header': 'value'},
            raw_headers={'RAW': 'HEADER'},
            filter=_filter,
            limit=9,
            offset=10)

        self.assertEqual(resp, {"test": "result"})
        self.assert_called_with('SoftLayer_SERVICE', 'METHOD',
                                mask={'object': {'attribute': ''}},
                                filter=_filter,
                                identifier=5678,
                                args=(1234,),
                                limit=9,
                                offset=10,
                                )
        calls = self.calls('SoftLayer_SERVICE', 'METHOD')
        self.assertEqual(len(calls), 1)
        self.assertIn('header', calls[0].headers)
        self.assertEqual(calls[0].headers['header'], 'value')

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
        _call.side_effect = [list(range(100)), list(range(100, 125))]
        result = list(self.client.iter_call('SERVICE', 'METHOD', iter=True))

        self.assertEqual(list(range(125)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=0),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=100),
        ])
        _call.reset_mock()

        # chunk=100, no limit. Requires one extra request.
        _call.side_effect = [list(range(100)), list(range(100, 200)), []]
        result = list(self.client.iter_call('SERVICE', 'METHOD', iter=True))
        self.assertEqual(list(range(200)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=0),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=100),
            mock.call('SERVICE', 'METHOD', limit=100, iter=False, offset=200),
        ])
        _call.reset_mock()

        # chunk=25, limit=30
        _call.side_effect = [list(range(0, 25)), list(range(25, 30))]
        result = list(self.client.iter_call(
            'SERVICE', 'METHOD', iter=True, limit=30, chunk=25))
        self.assertEqual(list(range(30)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', iter=False, limit=25, offset=0),
            mock.call('SERVICE', 'METHOD', iter=False, limit=5, offset=25),
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

        # chunk=25, limit=30, offset=12
        _call.side_effect = [list(range(0, 25)), list(range(25, 30))]
        result = list(self.client.iter_call('SERVICE', 'METHOD', 'ARG',
                                            iter=True,
                                            limit=30,
                                            chunk=25,
                                            offset=12))
        self.assertEqual(list(range(30)), result)
        _call.assert_has_calls([
            mock.call('SERVICE', 'METHOD', 'ARG',
                      iter=False, limit=25, offset=12),
            mock.call('SERVICE', 'METHOD', 'ARG',
                      iter=False, limit=5, offset=37),
        ])

        # Chunk size of 0 is invalid
        self.assertRaises(
            AttributeError,
            lambda: list(self.client.iter_call('SERVICE', 'METHOD',
                                               iter=True, chunk=0)))

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
