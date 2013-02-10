import sys
import os
import os.path
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from mock import patch, MagicMock
from argparse import ArgumentParser, Namespace

import SoftLayer
import SoftLayer.CLI
import prettytable

if sys.version_info >= (3,):
    raw_input_path = 'builtins.input'
else:
    raw_input_path = '__builtin__.raw_input'


FIXTURE_PATH = os.path.abspath(os.path.join(__file__, '..', '..', 'fixtures'))


class PromptTests(unittest.TestCase):

    @patch(raw_input_path)
    def test_invalid_response(self, raw_input_mock):
        raw_input_mock.return_value = 'y'
        result = SoftLayer.CLI.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertFalse(result)

        raw_input_mock.return_value = 'wakakwakwaka'
        result = SoftLayer.CLI.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertFalse(result)

        raw_input_mock.return_value = ''
        result = SoftLayer.CLI.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertEqual(result, None)

    @patch(raw_input_path)
    def test_valid_response(self, raw_input_mock):
        raw_input_mock.return_value = 'n'
        result = SoftLayer.CLI.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertTrue(result)

        raw_input_mock.return_value = 'N'
        result = SoftLayer.CLI.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertTrue(result)

    def test_prettytable_helper(self):
        t = SoftLayer.CLI.Table(['one', 'two'])
        self.assertEqual(t.horizontal_char, '.')
        self.assertEqual(t.vertical_char, ':')
        self.assertEqual(t.junction_char, ':')

    @patch(raw_input_path)
    def test_do_or_die(self, raw_input_mock):
        confirmed = '37347373737'
        raw_input_mock.return_value = confirmed
        result = SoftLayer.CLI.no_going_back(confirmed)
        self.assertTrue(result)

        confirmed = None
        raw_input_mock.return_value = ''
        result = SoftLayer.CLI.no_going_back(confirmed)
        self.assertFalse(result)

    def test_clirunnable_exercise(self):
        res = SoftLayer.CLI.CLIRunnable.add_additional_args(None)
        self.assertEqual(res, None)
        res = SoftLayer.CLI.CLIRunnable.execute(None, None)
        self.assertEqual(res, None)

    @patch(raw_input_path)
    def test_confirmation(self, raw_input_mock):
        raw_input_mock.return_value = 'Y'
        res = SoftLayer.CLI.confirm(allow_empty=False, default=False)
        self.assertTrue(res)

        raw_input_mock.return_value = 'N'
        res = SoftLayer.CLI.confirm(allow_empty=False, default=False)
        self.assertFalse(res)

        raw_input_mock.return_value = ''
        res = SoftLayer.CLI.confirm(allow_empty=True, default=True)
        self.assertTrue(res)

    def test_no_tty(self):
        class fake(object):
            pass
        args = fake()
        args.fmt = 'raw'

        t = SoftLayer.CLI.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.hrules = prettytable.FRAME
        ret = SoftLayer.CLI.format_output(t, args)

        self.assertFalse(ret.border)
        self.assertFalse(ret.header)
        self.assertNotEqual(ret.hrules, t.hrules)
        # self.assertNotEqual(ret.align, t.argslign)

    def test_prettytable(self):
        class fake(object):
            pass
        args = fake()
        args.fmt = 'table'

        t = SoftLayer.CLI.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.hrules = prettytable.FRAME
        ret = SoftLayer.CLI.format_output(t, args)

        self.assertEqual(ret.hrules, t.hrules)
        self.assertEqual(ret.align, t.align)

    def test_add_really_argument(self):
        parser = ArgumentParser()
        SoftLayer.CLI.add_really_argument(parser)
        args = parser.parse_args(['--really'])
        self.assertTrue(args.really)

    @patch('sys.stdout.isatty')
    def test_add_fmt_argument_isatty(self, isatty):
        isatty.return_value = True
        parser = ArgumentParser()
        SoftLayer.CLI.add_fmt_argument(parser)
        args = parser.parse_args(['--format=raw'])
        self.assertEqual('raw', args.fmt)

        args = parser.parse_args([])
        self.assertEqual('table', args.fmt)

    @patch('sys.stdout.isatty')
    def test_add_fmt_argument(self, isatty):
        isatty.return_value = False
        parser = ArgumentParser()
        SoftLayer.CLI.add_fmt_argument(parser)
        args = parser.parse_args(['--format=raw'])
        self.assertEqual('raw', args.fmt)

        args = parser.parse_args([])
        self.assertEqual('raw', args.fmt)


class TestParseArgs(unittest.TestCase):
    @patch('sys.stdout.isatty')
    def test_primary(self, isatty):
        isatty.return_value = False
        module_name, parent_args, aux_args = SoftLayer.CLI.parse_primary_args(
            ['module', 'module2'], ['module'])

        self.assertEqual('module', module_name)
        self.assertEqual([], aux_args)

    @patch('sys.exit')
    def test_primary_help(self, ext):
        return_value = SoftLayer.CLI.parse_primary_args(
            ['module', 'module2'], [])
        ext.assert_called_with(1)
        self.assertEqual(ext(), return_value)

        return_value = SoftLayer.CLI.parse_primary_args(
            ['module', 'module2'], ['--help'])
        ext.assert_called_with(1)
        self.assertEqual(ext(), return_value)

    @patch('sys.exit')
    def test_module_empty(self, ext):
        # module, module_name, actions, posargs, argv
        module = MagicMock()
        module.__doc__ = 'some info'
        action = MagicMock()
        SoftLayer.CLI.parse_module_args(
            module, 'module', {'action': action}, [], [])
        ext.assert_called_with(2)

    def test_module_action(self):
        # module, module_name, actions, posargs, argv
        module = MagicMock()
        module.__doc__ = 'some info'
        action = MagicMock()
        args = SoftLayer.CLI.parse_module_args(
            module, 'module', {'action': action}, ['action'], [])
        self.assertEqual('action', args.action)
        self.assertEqual(None, args.config)
        self.assertEqual('raw', args.fmt)

    def test_module_with_options(self):
        # module, module_name, actions, posargs, argv
        module = MagicMock()
        module.__doc__ = 'some info'
        action = MagicMock()
        args = SoftLayer.CLI.parse_module_args(
            module, 'module', {'action': action},
            ['action'], ['--format=table', '--config=/path/to/config'])
        self.assertEqual('action', args.action)
        self.assertEqual('/path/to/config', args.config)
        self.assertEqual('table', args.fmt)

    def test_module_with_base(self):
        # module, module_name, actions, posargs, argv
        module = MagicMock()
        module.__doc__ = 'some info'
        action = MagicMock()
        args = SoftLayer.CLI.parse_module_args(
            module, 'module', {None: action}, [], [])
        self.assertEqual(None, args.action)
        self.assertEqual(None, args.config)
        self.assertEqual('raw', args.fmt)


class TestExecuteCommand(unittest.TestCase):

    def test_execute_command_table(self):
        f = MagicMock()
        f.execute.return_value = \
            SoftLayer.CLI.Table()
        args = Namespace(fmt='raw')
        SoftLayer.CLI.execute_action(f, args=args)

    def test_execute_command_none(self):
        f = MagicMock()
        f.execute.return_value = None
        SoftLayer.CLI.execute_action(f)

    @patch('sys.exit')
    def test_execute_command_exception(self, ext):
        f = MagicMock()
        f.execute.side_effect = SoftLayer.SoftLayerError()
        SoftLayer.CLI.execute_action(f)


class TestParseConfig(unittest.TestCase):

    def test_parse_config_no_files(self):
        config = SoftLayer.CLI.parse_config([])
        self.assertEqual({}, config)

    def test_parse_config_no_softlayer_section(self):
        path = os.path.join(FIXTURE_PATH, 'empty.conf')
        config = SoftLayer.CLI.parse_config([path])
        self.assertEqual({}, config)

    def test_parse_config_empty(self):
        path = os.path.join(FIXTURE_PATH, 'no_options.conf')
        config = SoftLayer.CLI.parse_config([path])
        self.assertEqual({}, config)

    def test_parse_config(self):
        path = os.path.join(FIXTURE_PATH, 'full.conf')
        config = SoftLayer.CLI.parse_config([path])
        self.assertEqual({
            'username': 'myusername',
            'api_key': 'myapi_key',
            'endpoint_url': 'myendpoint_url'
        }, config)


class DynamicImportTests(unittest.TestCase):

    def test_action_list(self):
        actions = SoftLayer.CLI.action_list()
        self.assertIn('cci', actions)
        self.assertIn('dns', actions)

    def test_runnable_type(self):
        class TestCommand(SoftLayer.CLI.CLIRunnable):
            action = 'test'
        self.assertEqual(
            SoftLayer.CLI.plugins, {'cli_helper_tests': {'test': TestCommand}})
