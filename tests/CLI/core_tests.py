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
        for path, cmd in recursive_subcommand_loader(core.cli,
                                                     current_path='root'):
            try:
                cmd.main(args=['--help'])
            except SystemExit as ex:
                if ex.code != 0:
                    self.fail("Non-zero exit code for command: %s" % path)

    def test_verbose_max(self):
        with mock.patch('logging.getLogger') as log_mock:
            result = self.run_command(['-vvv', 'vs', 'list'])

            self.assert_no_fail(result)
            log_mock().addHandler.assert_called_with(mock.ANY)
            log_mock().setLevel.assert_called_with(logging.DEBUG)

    def test_build_client(self):
        env = environment.Environment()
        result = self.run_command(['vs', 'list'], env=env)

        self.assert_no_fail(result)
        self.assertIsNotNone(env.client)

    def test_diagnostics(self):
        result = self.run_command(['-v', 'vs', 'list'])

        self.assert_no_fail(result)
        self.assertIn('SoftLayer_Account::getVirtualGuests', result.output)
        self.assertIn('"execution_time"', result.output)
        self.assertIn('"api_calls"', result.output)
        self.assertIn('"version"', result.output)
        self.assertIn('"python_version"', result.output)
        self.assertIn('"library_location"', result.output)


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


def recursive_subcommand_loader(root, current_path=''):
    """Recursively load and list every command."""

    if getattr(root, 'list_commands', None) is None:
        return

    ctx = click.Context(root)

    for command in root.list_commands(ctx):
        new_path = '%s:%s' % (current_path, command)
        logging.info("loading %s", new_path)
        new_root = root.get_command(ctx, command)
        if new_root is None:
            raise Exception('Could not load command: %s' % command)

        for path, cmd in recursive_subcommand_loader(new_root,
                                                     current_path=new_path):
            yield path, cmd
        yield current_path, new_root
