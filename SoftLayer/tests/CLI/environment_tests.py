"""
    SoftLayer.tests.CLI.environment_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import click
import mock

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer import testing


class EnvironmentTests(testing.TestCase):

    def set_up(self):
        self.env = environment.Environment()

    def test_module_list(self):
        actions = self.env.module_list()
        self.assertIn('vs', actions)
        self.assertIn('dns', actions)

    @mock.patch('SoftLayer.utils.console_input')
    def test_input(self, raw_input_mock):
        r = self.env.input('input')
        raw_input_mock.assert_called_with('input')
        self.assertEqual(raw_input_mock(), r)

    @mock.patch('getpass.getpass')
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
        self.assertRaises(exceptions.InvalidCommand,
                          self.env.get_command, 'invalid', 'command')

    def test_get_command(self):
        self.env.plugins = {'vs': {'list': 'something'}}
        command = self.env.get_command('vs', 'list')
        self.assertIsInstance(command, click.Command)
