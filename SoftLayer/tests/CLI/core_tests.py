"""
    SoftLayer.tests.CLI.core_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import logging

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
        self.assertIn('"method": "getVirtualGuests",', result.output)
        self.assertIn('"service": "Account",', result.output)
        self.assertIn('"time":', result.output)


class CoreMainTests(testing.TestCase):

    @mock.patch('SoftLayer.CLI.core.cli.main')
    @mock.patch('sys.stdout', new_callable=utils.StringIO)
    def test_unexpected_error(self, stdoutmock, climock):
        climock.side_effect = AttributeError('Attribute foo does not exist')

        with self.assertRaises(SystemExit):
            core.main()

        self.assertIn("Feel free to report this error as it is likely a bug",
                      stdoutmock.getvalue())
        self.assertIn("Traceback (most recent call last)",
                      stdoutmock.getvalue())
        self.assertIn("AttributeError: Attribute foo does not exist",
                      stdoutmock.getvalue())


def recursive_subcommand_loader(root, path=''):
    if getattr(root, 'list_commands', None) is None:
        return

    ctx = click.Context(root)

    for command in root.list_commands(ctx):
        new_root = root.get_command(ctx, command)
        new_path = '%s:%s' % (path, command)
        recursive_subcommand_loader(new_root, path=new_path)
        logging.info('loading %s', new_path)
