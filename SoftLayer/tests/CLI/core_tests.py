"""
    SoftLayer.tests.CLI.core_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from mock import MagicMock, patch

import SoftLayer

from SoftLayer.tests import TestCase
from SoftLayer.CLI import core
from SoftLayer.CLI.helpers import CLIAbort
from SoftLayer.CLI.environment import Environment, InvalidModule, CLIRunnable


def module_fixture():
    """
usage: sl vs <command> [<args>...] [options]
       sl vs [-h | --help]
"""


def module_no_command_fixture():
    """
usage: sl vs [<args>...] [options]
       sl vs [-h | --help]
"""


class SubmoduleFixture(CLIRunnable):
    """
usage: sl vs list [options]

Options:
  --hourly  Show hourly instances
"""
    options = []

    def execute(self, args):
        return "test"


class EnvironmentFixture(Environment):
    def __init__(self):
        super(EnvironmentFixture, self).__init__()
        self.plugins = {'vs': {'list': SubmoduleFixture}}
        self.aliases = {
            'meta': 'metadata',
            'my': 'metadata',
        }
        self.config = {}

    def load_module(self, *args, **kwargs):
        return module_fixture

    def plugin_list(self, *args, **kwargs):
        return self.plugins.keys()


class CommandLineTests(TestCase):
    def set_up(self):
        self.env = EnvironmentFixture()
        self.env.get_module_name = MagicMock()

    def test_normal_path(self):
        self.env.get_module_name.return_value = 'vs'
        self.assertRaises(
            SystemExit, core.main,
            args=['vs', 'list', '--config=path/to/config'],
            env=self.env)
        self.assertRaises(
            SystemExit, core.main,
            args=['vs', 'nope', '--config=path/to/config'], env=self.env)
        self.assertRaises(
            SystemExit, core.main,
            args=['vs', 'list', '--format=totallynotvalid'], env=self.env)

    @patch('SoftLayer.TimedClient.get_last_calls')
    def test_normal_path_with_timings(self, calls_mock):
        calls_mock.return_value = [('SERVICE.METHOD', 1000, 0.25)]
        self.env.get_module_name.return_value = 'vs'
        self.assertRaises(
            SystemExit, core.main,
            args=['vs', 'list', '--config=path/to/config', '--timings'],
            env=self.env)
        calls_mock.assert_called()

    @patch('logging.getLogger')
    @patch('logging.StreamHandler')
    def test_with_debug(self, stream_handler, logger):
        self.env.get_module_name.return_value = 'vs'
        self.assertRaises(
            SystemExit, core.main,
            args=['vs', 'list', '--debug=3'],
            env=self.env)
        logger().setLevel.assert_called_with(10)
        logger().addHandler.assert_called_with(stream_handler())

    def test_invalid_module(self):
        self.env.get_module_name.return_value = 'nope'
        self.assertRaises(
            SystemExit, core.main,
            args=['nope', 'list', '--config=path/to/config'], env=self.env)

    def test_module_with_no_command(self):
        self.env.plugins = {
            'vs': {'list': SubmoduleFixture, None: SubmoduleFixture}
        }
        self.env.get_module_name.return_value = 'vs'
        self.env.load_module = MagicMock()
        self.env.load_module.return_value = module_no_command_fixture
        resolver = core.CommandParser(self.env)
        command, command_args = resolver.parse(['vs', 'list'])
        self.assertEqual(SubmoduleFixture, command)

    def test_main(self):
        self.env.get_module_name.return_value = 'vs'
        self.env.plugins = {
            'vs': {'list': SubmoduleFixture}
        }
        self.assertRaises(
            SystemExit, core.main,
            args=['vs', 'list'],
            env=self.env)

    def test_help(self):
        self.env.get_module_name.return_value = 'help'
        self.assertRaises(
            SystemExit, core.main,
            args=['help', 'vs', '--config=path/to/config'], env=self.env)

    def test_keyboard_interrupt(self):
        self.env.get_module_name.side_effect = KeyboardInterrupt
        self.assertRaises(
            SystemExit, core.main, args=['vs', 'list'], env=self.env)

    def test_abort(self):
        self.env.get_module_name.side_effect = CLIAbort('exit!')
        self.assertRaises(
            SystemExit, core.main, args=['vs', 'list'], env=self.env)

    def test_invalid_module_error(self):
        self.env.get_module_name.side_effect = InvalidModule('vs')
        self.assertRaises(
            SystemExit, core.main, args=['vs', 'list'], env=self.env)

    def test_softlayer_error(self):
        self.env.get_module_name.side_effect = SoftLayer.SoftLayerError
        self.assertRaises(
            SystemExit, core.main, args=['vs', 'list'], env=self.env)

    def test_softlayer_api_error(self):
        error = SoftLayer.SoftLayerAPIError('Exception', 'Exception Text')
        self.env.get_module_name.side_effect = error
        self.assertRaises(
            SystemExit, core.main, args=['vs', 'list'], env=self.env)

    def test_softlayer_api_error_authentication_error(self):
        error = SoftLayer.SoftLayerAPIError('SoftLayerException',
                                            'Invalid API Token')
        self.env.get_module_name.side_effect = error
        self.assertRaises(
            SystemExit, core.main, args=['vs', 'list'], env=self.env)

    def test_system_exit_error(self):
        self.env.get_module_name.side_effect = SystemExit
        self.assertRaises(
            SystemExit, core.main, args=['vs', 'list'], env=self.env)

    @patch('traceback.format_exc')
    def test_uncaught_error(self, m):
        # Exceptions not caught should just Exit
        errors = [TypeError, RuntimeError, NameError, OSError, SystemError]
        for err in errors:
            m.reset_mock()
            m.return_value = 'testing'
            self.env.get_module_name.side_effect = err
            self.assertRaises(
                SystemExit, core.main, args=['vs', 'list'], env=self.env)
            m.assert_called_once_with()


class TestCommandParser(TestCase):
    def set_up(self):
        self.env = EnvironmentFixture()
        self.parser = core.CommandParser(self.env)

    def test_main(self,):
        args = self.parser.parse_main_args(
            args=['vs', 'list'])

        self.assertEqual(args['help'], False)
        self.assertEqual(args['<module>'], 'vs')
        self.assertEqual(args['<args>'], ['list'])

    def test_primary_help(self):
        args = self.parser.parse_main_args(args=[])
        self.assertEqual({
            '--help': False,
            '-h': False,
            '<args>': [],
            '<module>': None,
            '<command>': None,
            'help': False,
        }, args)

        args = self.parser.parse_main_args(args=['help'])
        self.assertEqual({
            '--help': False,
            '-h': False,
            '<args>': [],
            '<module>': 'help',
            '<command>': None,
            'help': False,
        }, args)

        args = self.parser.parse_main_args(args=['help', 'module'])
        self.assertEqual({
            '--help': False,
            '-h': False,
            '<args>': ['module'],
            '<module>': 'help',
            '<command>': None,
            'help': False,
        }, args)

        self.assertRaises(
            SystemExit, self.parser.parse_main_args, args=['--help'])

    @patch('sys.stdout.isatty', return_value=True)
    def test_tty(self, tty):
        self.assertRaises(
            SystemExit, self.parser.parse_command_args, 'vs', 'list', [])

    def test_confirm(self):
        command = MagicMock()
        command.options = ['confirm']
        command.__doc__ = 'usage: sl vs list [options]'
        self.env.get_command = MagicMock()
        self.env.get_command.return_value = command
        self.assertRaises(
            SystemExit, self.parser.parse_command_args, 'vs', 'list', [])
