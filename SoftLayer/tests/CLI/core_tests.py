"""
    SoftLayer.tests.CLI.core_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import os
import os.path
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
from mock import MagicMock, patch

import SoftLayer
import SoftLayer.CLI as cli
from SoftLayer.CLI.helpers import CLIAbort
from SoftLayer.CLI.environment import Environment, InvalidModule


def module_fixture():
    """
usage: sl cci <command> [<args>...] [options]
       sl cci [-h | --help]
"""


class submodule_fixture(object):
    """
usage: sl cci list [options]

Options:
  --hourly                   Show hourly instances
"""
    options = []

    @staticmethod
    def execute(client, args):
        return "test"


class EnvironmentFixture(Environment):
    plugins = {'cci': {'list': submodule_fixture}}
    aliases = {
        'meta': 'metadata',
        'my': 'metadata',
    }
    config = {}

    def load_module(self, *args, **kwargs):
        return module_fixture

    def plugin_list(self, *args, **kwargs):
        return self.plugins.keys()


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentFixture()
        self.env.get_module_name = MagicMock()

    def test_normal_path(self):
        self.env.get_module_name.return_value = 'cci'
        self.assertRaises(
            SystemExit, cli.core.main,
            args=['cci', 'list', '--config=path/to/config'], env=self.env)
        self.assertRaises(
            SystemExit, cli.core.main,
            args=['cci', 'nope', '--config=path/to/config'], env=self.env)
        self.assertRaises(
            SystemExit, cli.core.main,
            args=['cci', 'list', '--format=totallynotvalid'], env=self.env)

    def test_invalid_module(self):
        self.env.get_module_name.return_value = 'nope'
        self.assertRaises(
            SystemExit, cli.core.main,
            args=['nope', 'list', '--config=path/to/config'], env=self.env)

    def test_help(self):
        self.env.get_module_name.return_value = 'help'
        self.assertRaises(
            SystemExit, cli.core.main,
            args=['help', 'cci', '--config=path/to/config'], env=self.env)

    def test_keyboard_interrupt(self):
        self.env.get_module_name.side_effect = KeyboardInterrupt
        self.assertRaises(
            SystemExit, cli.core.main, args=['cci', 'list'], env=self.env)

    def test_abort(self):
        self.env.get_module_name.side_effect = CLIAbort('exit!')
        self.assertRaises(
            SystemExit, cli.core.main, args=['cci', 'list'], env=self.env)

    def test_invalid_module_error(self):
        self.env.get_module_name.side_effect = InvalidModule('cci')
        self.assertRaises(
            SystemExit, cli.core.main, args=['cci', 'list'], env=self.env)

    def test_softlayer_error(self):
        self.env.get_module_name.side_effect = SoftLayer.SoftLayerError
        self.assertRaises(
            SystemExit, cli.core.main, args=['cci', 'list'], env=self.env)

    def test_system_exit_error(self):
        self.env.get_module_name.side_effect = SystemExit
        self.assertRaises(
            SystemExit, cli.core.main, args=['cci', 'list'], env=self.env)

    def test_value_key_errors(self):
        self.env.get_module_name.side_effect = ValueError
        self.assertRaises(
            ValueError, cli.core.main, args=['cci', 'list'], env=self.env)

        self.env.get_module_name.side_effect = KeyError
        self.assertRaises(
            KeyError, cli.core.main, args=['cci', 'list'], env=self.env)

    @patch('traceback.format_exc')
    def test_uncaught_error(self, m):
        # Exceptions not caught should just Exit
        errors = [TypeError, RuntimeError, NameError, OSError, SystemError]
        for err in errors:
            m.reset_mock()
            m.return_value = 'testing'
            self.env.get_module_name.side_effect = err
            self.assertRaises(
                SystemExit, cli.core.main, args=['cci', 'list'], env=self.env)
            m.assert_called_once_with()


class TestCommandParser(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentFixture()
        self.parser = cli.core.CommandParser(self.env)

    def test_main(self,):
        args = self.parser.parse_main_args(
            args=['cci', 'list'])

        self.assertEqual(args['help'], False)
        self.assertEqual(args['<module>'], 'cci')
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
            SystemExit, self.parser.parse_command_args, 'cci', 'list', [])

    def test_confirm(self):
        command = MagicMock()
        command.options = ['confirm']
        command.__doc__ = 'usage: sl cci list [options]'
        self.env.get_command = MagicMock()
        self.env.get_command.return_value = command
        self.assertRaises(
            SystemExit, self.parser.parse_command_args, 'cci', 'list', [])


class TestFormatOutput(unittest.TestCase):
    def test_format_output_string(self):
        t = cli.core.format_output('just a string', 'raw')
        self.assertEqual('just a string', t)

        t = cli.core.format_output(u'just a string', 'raw')
        self.assertEqual(u'just a string', t)

    def test_format_output_raw(self):
        t = cli.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.sortby = 'nothing'
        ret = cli.core.format_output(t, 'raw')

        self.assertNotIn('nothing', str(ret))
        self.assertIn('testdata', str(ret))

    def test_format_output_formatted_item(self):
        item = cli.FormattedItem('test', 'test_formatted')
        ret = cli.core.format_output(item, 'table')
        self.assertEqual('test_formatted', ret)

    def test_format_output_list(self):
        item = ['this', 'is', 'a', 'list']
        ret = cli.core.format_output(item, 'table')
        self.assertEqual(os.linesep.join(item), ret)

    def test_format_output_table(self):
        t = cli.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.sortby = 'nothing'
        ret = cli.core.format_output(t, 'table')

        self.assertIn('nothing', str(ret))
        self.assertIn('testdata', str(ret))

    def test_unknown(self):
        t = cli.core.format_output({}, 'raw')
        self.assertEqual('{}', t)

    def test_sequentialoutput(self):
        t = cli.core.SequentialOutput(blanks=False)
        self.assertTrue(hasattr(t, 'append'))
        t.append('This is a test')
        t.append('')
        t.append('More tests')
        output = cli.core.format_output(t)
        self.assertEqual("This is a test\nMore tests", output)

        t.blanks = True
        output = cli.core.format_output(t)
        self.assertEqual("This is a test\n\nMore tests", output)
