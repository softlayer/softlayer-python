"""
    SoftLayer.tests.config_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
from mock import patch, Mock, ANY
import sys

from SoftLayer.config import (
    get_client_settings_args, get_client_settings_env,
    get_client_settings_config_file, get_client_settings)
from SoftLayer.tests import unittest

if sys.version_info >= (3,):
    config_parser_path = 'configparser'
else:
    config_parser_path = 'ConfigParser'


class TestGetClientSettings(unittest.TestCase):

    @patch('SoftLayer.config.setting_resolvers', [])
    def test_no_resolvers(self):
        result = get_client_settings()
        self.assertEqual(result, {})

    def test_resolve_one(self):
        resolvers = [Mock() for i in range(1)]
        resolvers[0].return_value = {'auth': 'AUTH HANDLER'}
        with patch('SoftLayer.config.setting_resolvers', resolvers):
            result = get_client_settings()
            self.assertEqual(result, {'auth': 'AUTH HANDLER'})

    def test_inherit(self):
        # This tests the inheritting properties of the list of resolvers.
        # Values should be preferred on earlier resolvers except where their
        # value is false-ish
        resolvers = [Mock() for i in range(4)]
        resolvers[0].return_value = {'timeout': 20}
        resolvers[1].return_value = {'timeout': 10, 'auth': None}
        resolvers[2].return_value = None
        resolvers[3].return_value = {'auth': 'AUTH HANDLER'}
        with patch('SoftLayer.config.setting_resolvers', resolvers):
            result = get_client_settings()
            self.assertEqual(result, {'auth': 'AUTH HANDLER', 'timeout': 20})


class TestGetClientSettingsArgs(unittest.TestCase):

    def test_username_api_key(self):
        result = get_client_settings_args(username='username',
                                          api_key='api_key',
                                          endpoint_url='http://endpoint/',
                                          timeout=10)

        self.assertEqual(result['endpoint_url'], 'http://endpoint/')
        self.assertEqual(result['timeout'], 10)
        self.assertEqual(result['auth'].username, 'username')
        self.assertEqual(result['auth'].api_key, 'api_key')

    def test_no_auth(self):
        result = get_client_settings_args()

        self.assertEqual(result, {
            'endpoint_url': None,
            'timeout': None,
            'auth': None,
        })

    def test_with_auth(self):
        auth = Mock()
        result = get_client_settings_args(auth=auth)

        self.assertEqual(result['endpoint_url'], None)
        self.assertEqual(result['timeout'], None)
        self.assertEqual(result['auth'], auth)


class TestGetClientSettingsEnv(unittest.TestCase):

    @patch.dict('os.environ', {'SL_USERNAME': 'username',
                               'SL_API_KEY': 'api_key'})
    def test_username_api_key(self):
        result = get_client_settings_env()

        self.assertEqual(result['auth'].username, 'username')
        self.assertEqual(result['auth'].api_key, 'api_key')

    @patch.dict('os.environ', {'SL_USERNAME': '', 'SL_API_KEY': ''})
    def test_no_auth(self):
        result = get_client_settings_env()

        self.assertIsNone(result)


class TestGetClientSettingsConfigFile(unittest.TestCase):

    @patch('%s.RawConfigParser' % config_parser_path)
    def test_username_api_key(self, config_parser):
        result = get_client_settings_config_file()

        self.assertEqual(result['endpoint_url'], config_parser().get())
        self.assertEqual(result['timeout'], config_parser().get())
        self.assertEqual(result['auth'].username, config_parser().get())
        self.assertEqual(result['auth'].api_key, config_parser().get())

    @patch('%s.RawConfigParser' % config_parser_path)
    def test_no_section(self, config_parser):
        config_parser().has_section.return_value = False
        result = get_client_settings_config_file()

        self.assertIsNone(result)

    @patch('%s.RawConfigParser' % config_parser_path)
    def test_config_file(self, config_parser):
        get_client_settings_config_file(config_file='path/to/config')
        config_parser().read.assert_called_with([ANY, ANY, 'path/to/config'])
