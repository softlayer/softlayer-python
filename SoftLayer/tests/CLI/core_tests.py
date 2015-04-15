"""
    SoftLayer.tests.CLI.core_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import logging

import SoftLayer
from SoftLayer.CLI import core
from SoftLayer.CLI import environment
from SoftLayer import testing
from SoftLayer import utils

import click
import mock


class CoreTests(testing.TestCase):

    def test_load_all(self):
        recursive_subcommand_loader(core.cli, path='root')

    def test_debug_max(self):
        with mock.patch('logging.getLogger') as log_mock:
            result = self.run_command(['--debug=3', 'vs', 'list'])

            self.assertEqual(result.exit_code, 0)
            log_mock().addHandler.assert_called_with(mock.ANY)
            log_mock().setLevel.assert_called_with(logging.DEBUG)

    def test_verbose_max(self):
        with mock.patch('logging.getLogger') as log_mock:
            result = self.run_command(['-vvv', 'vs', 'list'])

            self.assertEqual(result.exit_code, 0)
            log_mock().addHandler.assert_called_with(mock.ANY)
            log_mock().setLevel.assert_called_with(logging.DEBUG)

    def test_build_client(self):
        env = environment.Environment()
        result = self.run_command(['vs', 'list'], env=env)

        self.assertEqual(result.exit_code, 0)
        self.assertIsNotNone(env.client)

    def test_timings(self):
        result = self.run_command(['--timings', 'vs', 'list'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('"method": "getVirtualGuests"', result.output)
        self.assertIn('"service": "SoftLayer_Account"', result.output)
        self.assertIn('"time":', result.output)


class CoreMainTests(testing.TestCase):

    @mock.patch('SoftLayer.CLI.core.cli.main')
    @mock.patch('sys.stdout', new_callable=utils.StringIO)
    def test_unexpected_error(self, stdoutmock, climock):
        climock.side_effect = AttributeError('Attribute foo does not exist')

        self.assertRaises(SystemExit, core.main)

        self.assertIn("Feel free to report this error as it is likely a bug",
                      stdoutmock.getvalue())
        self.assertIn("Traceback (most recent call last)",
                      stdoutmock.getvalue())
        self.assertIn("AttributeError: Attribute foo does not exist",
                      stdoutmock.getvalue())

    @mock.patch('SoftLayer.CLI.core.cli.main')
    @mock.patch('sys.stdout', new_callable=utils.StringIO)
    def test_sl_error(self, stdoutmock, climock):
        ex = SoftLayer.SoftLayerAPIError('SoftLayer_Exception', 'Not found')
        climock.side_effect = ex

        self.assertRaises(SystemExit, core.main)

        self.assertIn("SoftLayerAPIError(SoftLayer_Exception): Not found",
                      stdoutmock.getvalue())

    @mock.patch('SoftLayer.CLI.core.cli.main')
    @mock.patch('sys.stdout', new_callable=utils.StringIO)
    def test_auth_error(self, stdoutmock, climock):
        ex = SoftLayer.SoftLayerAPIError('SoftLayer_Exception',
                                         'Invalid API token.')
        climock.side_effect = ex

        self.assertRaises(SystemExit, core.main)

        self.assertIn("Authentication Failed:", stdoutmock.getvalue())
        self.assertIn("use 'slcli config setup'", stdoutmock.getvalue())


def recursive_subcommand_loader(root, path=''):
    """Recursively load and list every command."""

    if getattr(root, 'list_commands', None) is None:
        return

    ctx = click.Context(root)

    for command in root.list_commands(ctx):
        new_path = '%s:%s' % (path, command)
        logging.info("loading %s", new_path)
        new_root = root.get_command(ctx, command)
        recursive_subcommand_loader(new_root, path=new_path)
