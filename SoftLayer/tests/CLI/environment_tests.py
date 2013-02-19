import sys
import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA
from mock import patch, MagicMock

from SoftLayer import API_PUBLIC_ENDPOINT
import SoftLayer.CLI as cli

if sys.version_info >= (3,):
    raw_input_path = 'builtins.input'
else:
    raw_input_path = '__builtin__.raw_input'
FIXTURE_PATH = os.path.abspath(os.path.join(__file__, '..', '..', 'fixtures'))


class EnvironmentTests(unittest.TestCase):

    def setUp(self):
        self.env = cli.environment.Environment()

    def test_plugin_list(self):
        actions = self.env.plugin_list()
        self.assertIn('cci', actions)
        self.assertIn('dns', actions)

    def test_out(self):
        self.env.stdout = MagicMock()
        self.env.out('TEXT OUTPUT')
        self.env.stdout.write.assert_any_call('TEXT OUTPUT')
        self.env.stdout.write.assert_any_call(os.linesep)

    def test_err(self):
        self.env.stderr = MagicMock()
        self.env.err('TEXT OUTPUT')
        self.env.stderr.write.assert_any_call('TEXT OUTPUT')
        self.env.stderr.write.assert_any_call(os.linesep)

    @patch(raw_input_path)
    def test_input(self, raw_input_mock):
        r = self.env.input('input')
        raw_input_mock.assert_called_with('input')
        self.assertEqual(raw_input_mock(), r)

    def test_parse_config_no_files(self):
        self.env.load_config([])
        self.assertEqual({}, self.env.config)

    def test_parse_config_no_softlayer_section(self):
        path = os.path.join(FIXTURE_PATH, 'empty.conf')
        self.env.load_config([path])
        self.assertEqual({}, self.env.config)

    @patch('os.environ', {})
    def test_parse_config_empty(self):
        path = os.path.join(FIXTURE_PATH, 'no_options.conf')
        self.env.load_config([path])
        self.assertEqual(
            {'endpoint_url': API_PUBLIC_ENDPOINT}, self.env.config)

    def test_parse_config(self):
        path = os.path.join(FIXTURE_PATH, 'full.conf')
        self.env.load_config([path])
        self.assertEqual({
            'username': 'myusername',
            'api_key': 'myapi_key',
            'endpoint_url': 'myendpoint_url'
        }, self.env.config)

    def test_get_module_name(self):
        self.env.aliases = {'aliasname': 'realname'}
        r = self.env.get_module_name('aliasname')
        self.assertEqual(r, 'realname')

        r = self.env.get_module_name('realname')
        self.assertEqual(r, 'realname')
