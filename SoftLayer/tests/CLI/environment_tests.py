"""
    SoftLayer.tests.CLI.environment_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
import sys
import os
from mock import patch, MagicMock

from SoftLayer.tests import unittest
from SoftLayer.CLI.environment import Environment, InvalidCommand

if sys.version_info >= (3,):
    raw_input_path = 'builtins.input'
else:
    raw_input_path = '__builtin__.raw_input'


class EnvironmentTests(unittest.TestCase):

    def setUp(self):
        self.env = Environment()

    def test_plugin_list(self):
        actions = self.env.plugin_list()
        self.assertIn('cci', actions)
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

    @patch(raw_input_path)
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
        self.assertRaises(InvalidCommand, self.env.get_command, 'cci', 'list')

    def test_get_command(self):
        self.env.plugins = {'cci': {'list': 'something'}}
        command = self.env.get_command('cci', 'list')
        self.assertEqual(command, 'something')

    def test_get_command_none(self):
        # If None is in the action list, anything that doesn't exist as a
        # command will return the value of the None key. This is to support
        # sl help any_module_name
        self.env.plugins = {'cci': {None: 'something'}}
        command = self.env.get_command('cci', 'something else')
        self.assertEqual(command, 'something')

    def test_exit(self):
        self.assertRaises(SystemExit, self.env.exit, 1)
