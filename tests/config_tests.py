"""
    SoftLayer.tests.config_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

from SoftLayer import config
from SoftLayer import testing


class TestGetClientSettings(testing.TestCase):

    @mock.patch('SoftLayer.config.SETTING_RESOLVERS', [])
    def test_no_resolvers(self):
        result = config.get_client_settings()
        self.assertEqual(result, {})

    def test_resolve_one(self):
        resolvers = [mock.Mock() for i in range(1)]
        resolvers[0].return_value = {'auth': 'AUTH HANDLER'}
        with mock.patch('SoftLayer.config.SETTING_RESOLVERS', resolvers):
            result = config.get_client_settings()
            self.assertEqual(result, {'auth': 'AUTH HANDLER'})

    def test_inherit(self):
        # This tests the inheritting properties of the list of resolvers.
        # Values should be preferred on earlier resolvers except where their
        # value is false-ish
        resolvers = [mock.Mock() for i in range(4)]
        resolvers[0].return_value = {'timeout': 20}
        resolvers[1].return_value = {'timeout': 10, 'auth': None}
        resolvers[2].return_value = None
        resolvers[3].return_value = {'auth': 'AUTH HANDLER'}
        with mock.patch('SoftLayer.config.SETTING_RESOLVERS', resolvers):
            result = config.get_client_settings()
            self.assertEqual(result, {'auth': 'AUTH HANDLER', 'timeout': 20})


class TestGetClientSettingsArgs(testing.TestCase):

    def test_username_api_key(self):
        result = config.get_client_settings_args(
            username='username',
            api_key='api_key',
            endpoint_url='http://endpoint/',
            timeout=10,
            proxy='https://localhost:3128')

        self.assertEqual(result['endpoint_url'], 'http://endpoint/')
        self.assertEqual(result['timeout'], 10)
        self.assertEqual(result['username'], 'username')
        self.assertEqual(result['api_key'], 'api_key')
        self.assertEqual(result['proxy'], 'https://localhost:3128')


class TestGetClientSettingsEnv(testing.TestCase):

    @mock.patch.dict('os.environ', {'SL_USERNAME': 'username',
                                    'SL_API_KEY': 'api_key',
                                    'https_proxy': 'https://localhost:3128'})
    def test_username_api_key(self):
        result = config.get_client_settings_env()

        self.assertEqual(result['username'], 'username')
        self.assertEqual(result['api_key'], 'api_key')


class TestGetClientSettingsConfigFile(testing.TestCase):

    @mock.patch('six.moves.configparser.RawConfigParser')
    def test_username_api_key(self, config_parser):
        result = config.get_client_settings_config_file()

        self.assertEqual(result['endpoint_url'], config_parser().get())
        self.assertEqual(result['timeout'], config_parser().getfloat())
        self.assertEqual(result['proxy'], config_parser().get())
        self.assertEqual(result['username'], config_parser().get())
        self.assertEqual(result['api_key'], config_parser().get())

    @mock.patch('six.moves.configparser.RawConfigParser')
    def test_no_section(self, config_parser):
        config_parser().has_section.return_value = False
        result = config.get_client_settings_config_file()

        self.assertIsNone(result)

    @mock.patch('six.moves.configparser.RawConfigParser')
    def test_config_file(self, config_parser):
        config.get_client_settings_config_file(config_file='path/to/config')
        config_parser().read.assert_called_with([mock.ANY,
                                                mock.ANY,
                                                'path/to/config'])
