"""
    SoftLayer.tests.CLI.environment_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import os
from mock import patch, MagicMock

from SoftLayer.tests import TestCase
from SoftLayer.CLI.environment import Environment, InvalidCommand


class EnvironmentTests(TestCase):

    def set_up(self):
        self.env = Environment()

    def test_plugin_list(self):
        actions = self.env.plugin_list()
        self.assertIn('vs', actions)
        self.assertIn('dns', actions)

    def test_add_plugin(self):
        m = MagicMock()
        m.action = 'add_plugin_action_test'
        self.env.add_plugin(m)

        self.assertEqual(self.env.plugins,
                         {'mock': {'add_plugin_action_test': m}})

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

    @patch('SoftLayer.CLI.environment.console_input')
    def test_input(self, raw_input_mock):
        r = self.env.input('input')
        raw_input_mock.assert_called_with('input')
        self.assertEqual(raw_input_mock(), r)

    @patch('getpass.getpass')
    def test_getpass(self, getpass):
        r = self.env.getpass('input')
        getpass.assert_called_with('input')
        self.assertEqual(getpass(), r)

    def test_get_module_name(self):
        self.env.aliases = {'aliasname': 'realname'}
        r = self.env.get_module_name('aliasname')
        self.assertEqual(r, 'realname')

        r = self.env.get_module_name('realname')
        self.assertEqual(r, 'realname')

    def test_get_command_invalid(self):
        self.assertRaises(InvalidCommand, self.env.get_command, 'vs', 'list')

    def test_get_command(self):
        self.env.plugins = {'vs': {'list': 'something'}}
        command = self.env.get_command('vs', 'list')
        self.assertEqual(command, 'something')

    def test_get_command_none(self):
        # If None is in the action list, anything that doesn't exist as a
        # command will return the value of the None key. This is to support
        # sl help any_module_name
        self.env.plugins = {'vs': {None: 'something'}}
        command = self.env.get_command('vs', 'something else')
        self.assertEqual(command, 'something')

    def test_exit(self):
        self.assertRaises(SystemExit, self.env.exit, 1)
