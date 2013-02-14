import os
import os.path
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from argparse import ArgumentParser
from mock import patch, MagicMock

import SoftLayer
import SoftLayer.CLI as cli

FIXTURE_PATH = os.path.abspath(os.path.join(__file__, '..', '..', 'fixtures'))


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.env = MagicMock()
        self.env.plugin_list.return_value = ['plugin']
        self.env.plugins = {'plugin': {'action': MagicMock()}}

    def test_normal_path(self):
        self.assertRaises(
            SystemExit, cli.core.main, args=['--help'], env=self.env)
        self.assertRaises(
            SystemExit, cli.core.main,
            args=['plugin', 'action', '--config=path/to/config'], env=self.env)
        self.assertRaises(
            SystemExit, cli.core.main, args=['plugin'], env=self.env)
        self.assertRaises(
            SystemExit, cli.core.main,
            args=['plugin', 'action'], env=self.env)
        self.assertRaises(
            SystemExit, cli.core.main,
            args=['plugin', 'doesntexist'], env=self.env)

    def test_keyboard_interrupt(self):
        self.env.plugin_list.side_effect = KeyboardInterrupt
        self.assertRaises(
            SystemExit, cli.core.main, args=['--help'], env=self.env)

    def test_softlayer_error(self):
        self.env.plugin_list.side_effect = SoftLayer.SoftLayerError
        self.assertRaises(
            SystemExit, cli.core.main, args=['--help'], env=self.env)


class TestParseArgs(unittest.TestCase):
    @patch('sys.stdout.isatty')
    def test_primary(self, isatty):
        isatty.return_value = False
        module_name, parent_args, aux_args = cli.core.parse_primary_args(
            ['module', 'module2'], ['module'])

        self.assertEqual('module', module_name)
        self.assertEqual([], aux_args)

    def test_primary_help(self):
        self.assertRaises(
            SystemExit, cli.core.parse_primary_args,
            ['module', 'module2'], [])

        self.assertRaises(
            SystemExit, cli.core.parse_primary_args,
            ['module', 'module2'], ['help'])

        self.assertRaises(
            SystemExit, cli.core.parse_primary_args,
            ['module', 'module2'], ['--help'])

    def test_module_empty(self):
        module = MagicMock()
        module.__doc__ = 'some info'
        action = MagicMock()
        self.assertRaises(
            SystemExit, cli.core.parse_module_args,
            module, 'module', {'action': action}, [], [])

    def test_module_action(self):
        module = MagicMock()
        module.__doc__ = 'some info'
        action = MagicMock()
        args = cli.core.parse_module_args(
            module, 'module', {'action': action}, ['action'], [])
        self.assertEqual('action', args.action)
        self.assertEqual(None, args.config)
        self.assertEqual('raw', args.fmt)

    def test_module_with_options(self):
        module = MagicMock()
        module.__doc__ = 'some info'
        action = MagicMock()
        args = cli.core.parse_module_args(
            module, 'module', {'action': action},
            ['action'], ['--format=table', '--config=/path/to/config'])
        self.assertEqual('action', args.action)
        self.assertEqual('/path/to/config', args.config)
        self.assertEqual('table', args.fmt)

    def test_module_no_action(self):
        module = MagicMock()
        module.__doc__ = 'some info'
        self.assertRaises(
            SystemExit, cli.core.parse_module_args,
            module, 'module', {}, [], [])


class TestParseConfig(unittest.TestCase):

    def test_parse_config_no_files(self):
        config = cli.core.parse_config([])
        self.assertEqual({}, config)

    def test_parse_config_no_softlayer_section(self):
        path = os.path.join(FIXTURE_PATH, 'empty.conf')
        config = cli.core.parse_config([path])
        self.assertEqual({}, config)

    def test_parse_config_empty(self):
        path = os.path.join(FIXTURE_PATH, 'no_options.conf')
        config = cli.core.parse_config([path])
        self.assertEqual({}, config)

    def test_parse_config(self):
        path = os.path.join(FIXTURE_PATH, 'full.conf')
        config = cli.core.parse_config([path])
        self.assertEqual({
            'username': 'myusername',
            'api_key': 'myapi_key',
            'endpoint_url': 'myendpoint_url'
        }, config)


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
        ret = cli.core.format_output(item, 'raw')
        self.assertEqual('test_formatted', ret)

    def test_format_output_table(self):
        t = cli.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.sortby = 'nothing'
        ret = cli.core.format_output(t, 'table')

        self.assertIn('nothing', str(ret))
        self.assertIn('testdata', str(ret))

    @patch('sys.stdout.isatty')
    def test_add_fmt_argument_isatty(self, isatty):
        isatty.return_value = True
        parser = ArgumentParser()
        cli.core.add_fmt_argument(parser)
        args = parser.parse_args(['--format=raw'])
        self.assertEqual('raw', args.fmt)

        args = parser.parse_args([])
        self.assertEqual('table', args.fmt)

    @patch('sys.stdout.isatty')
    def test_add_fmt_argument(self, isatty):
        isatty.return_value = False
        parser = ArgumentParser()
        cli.core.add_fmt_argument(parser)
        args = parser.parse_args(['--format=raw'])
        self.assertEqual('raw', args.fmt)

        args = parser.parse_args([])
        self.assertEqual('raw', args.fmt)
