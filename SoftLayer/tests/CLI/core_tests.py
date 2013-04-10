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


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.env = MagicMock()
        self.env.plugin_list.return_value = ['cci']
        self.env.plugins = {'cci': {'list': submodule_fixture}}
        self.env.load_module.return_value = module_fixture

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

    def test_softlayer_error(self):
        self.env.get_module_name.side_effect = SoftLayer.SoftLayerError
        self.assertRaises(
            SystemExit, cli.core.main, args=['cci', 'list'], env=self.env)

    def test_value_key_errors(self):
        self.env.get_module_name.side_effect = ValueError
        self.assertRaises(
            ValueError, cli.core.main, args=['cci', 'list'], env=self.env)

        self.env.get_module_name.side_effect = KeyError
        self.assertRaises(
            KeyError, cli.core.main, args=['cci', 'list'], env=self.env)


class TestParseMainArgs(unittest.TestCase):
    def test_main(self,):
        args = cli.core.parse_main_args(
            args=['cci', 'list'])

        self.assertEqual(args['help'], False)
        self.assertEqual(args['<command>'], 'cci')
        self.assertEqual(args['<args>'], ['list'])

    def test_primary_help(self):
        args = cli.core.parse_main_args(args=[])
        self.assertEqual({
            '--help': False,
            '-h': False,
            '<args>': [],
            '<command>': None,
            'help': False,
        }, args)

        args = cli.core.parse_main_args(args=['help'])
        self.assertEqual({
            '--help': False,
            '-h': False,
            '<args>': [],
            '<command>': 'help',
            'help': False,
        }, args)

        args = cli.core.parse_main_args(args=['help', 'module'])
        self.assertEqual({
            '--help': False,
            '-h': False,
            '<args>': ['module'],
            '<command>': 'help',
            'help': False,
        }, args)

        self.assertRaises(
            SystemExit, cli.core.parse_main_args, args=['--help'])


class TestParseSubmoduleArgs(unittest.TestCase):
    @patch('sys.stdout.isatty', return_value=True)
    def test_tty(self, tty):
        self.assertRaises(
            SystemExit, cli.core.parse_submodule_args, submodule_fixture, [])

    def test_confirm(self):
        submodule = MagicMock()
        submodule.options = ['confirm']
        submodule.__doc__ = 'usage: sl cci list [options]'
        self.assertRaises(
            SystemExit, cli.core.parse_submodule_args, submodule, [''])


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
