"""
    SoftLayer.tests.CLI.helper_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
from mock import patch

import SoftLayer.CLI as cli

if sys.version_info >= (3,):
    raw_input_path = 'builtins.input'
else:
    raw_input_path = '__builtin__.raw_input'


class PromptTests(unittest.TestCase):

    @patch(raw_input_path)
    def test_invalid_response(self, raw_input_mock):
        raw_input_mock.return_value = 'y'
        result = cli.helpers.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertFalse(result)

        raw_input_mock.return_value = 'wakakwakwaka'
        result = cli.helpers.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertFalse(result)

        raw_input_mock.return_value = ''
        result = cli.helpers.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertEqual(result, None)

    @patch(raw_input_path)
    def test_valid_response(self, raw_input_mock):
        raw_input_mock.return_value = 'n'
        result = cli.helpers.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertTrue(result)

        raw_input_mock.return_value = 'N'
        result = cli.helpers.valid_response('test', 'n')
        raw_input_mock.assert_called_with('test')
        self.assertTrue(result)

    @patch(raw_input_path)
    def test_do_or_die(self, raw_input_mock):
        confirmed = '37347373737'
        raw_input_mock.return_value = confirmed
        result = cli.no_going_back(confirmed)
        self.assertTrue(result)

        # no_going_back should cast int's to str()
        confirmed = '4712309182309'
        raw_input_mock.return_value = confirmed
        result = cli.no_going_back(int(confirmed))
        self.assertTrue(result)

        confirmed = None
        raw_input_mock.return_value = ''
        result = cli.no_going_back(confirmed)
        self.assertFalse(result)

    def test_clirunnable_exercise(self):
        res = cli.CLIRunnable.add_additional_args(None)
        self.assertEqual(res, None)
        res = cli.CLIRunnable.execute(None, None)
        self.assertEqual(res, None)

    @patch(raw_input_path)
    def test_confirmation(self, raw_input_mock):
        raw_input_mock.return_value = 'Y'
        res = cli.confirm('Confirm?', default=False)
        self.assertTrue(res)

        raw_input_mock.return_value = 'N'
        res = cli.confirm('Confirm?', default=False)
        self.assertFalse(res)

        raw_input_mock.return_value = ''
        res = cli.confirm('Confirm?', default=True)
        self.assertTrue(res)


class FormattedItemTests(unittest.TestCase):

    def test_init(self):
        item = cli.FormattedItem('test', 'test_formatted')
        self.assertEqual('test', item.original)
        self.assertEqual('test_formatted', item.formatted)
        self.assertEqual('test', str(item))

        item = cli.FormattedItem('test')
        self.assertEqual('test', item.original)
        self.assertEqual('test', item.formatted)
        self.assertEqual('test', str(item))

    def test_mb_to_gb(self):
        item = cli.mb_to_gb(1024)
        self.assertEqual(1024, item.original)
        self.assertEqual('1G', item.formatted)

        item = cli.mb_to_gb('1024')
        self.assertEqual('1024', item.original)
        self.assertEqual('1G', item.formatted)

        item = cli.mb_to_gb('1025.0')
        self.assertEqual('1025.0', item.original)
        self.assertEqual('1G', item.formatted)

        self.assertRaises(ValueError, cli.mb_to_gb, '1024string')

    def test_gb(self):
        item = cli.gb(2)
        self.assertEqual(2048, item.original)
        self.assertEqual('2G', item.formatted)

        item = cli.gb('2')
        self.assertEqual(2048, item.original)
        self.assertEqual('2G', item.formatted)

        item = cli.gb('2.0')
        self.assertEqual(2048, item.original)
        self.assertEqual('2G', item.formatted)

    def test_blank(self):
        item = cli.helpers.blank()
        self.assertEqual('NULL', item.original)
        self.assertEqual('-', item.formatted)


class CLIAbortTests(unittest.TestCase):

    def test_init(self):
        e = cli.helpers.CLIAbort("something")
        self.assertEqual(2, e.code)
        self.assertEqual("something", e.message)
        self.assertIsInstance(e, cli.helpers.CLIHalt)


class CLIRunnableTypeTests(unittest.TestCase):

    def test_runnable_type(self):
        cli.environment.CLIRunnableType.env = cli.environment.Environment()

        class TestCommand(cli.CLIRunnable):
            action = 'test'
        self.assertEqual(
            cli.environment.CLIRunnableType.env.plugins,
            {'helper_tests': {'test': TestCommand}})


class ResolveIdTests(unittest.TestCase):

    def test_resolve_id_one(self):
        resolver = lambda r: [12345]
        id = cli.helpers.resolve_id(resolver, 'test')

        self.assertEqual(id, 12345)

    def test_resolve_id_none(self):
        resolver = lambda r: []
        self.assertRaises(
            cli.helpers.CLIAbort, cli.helpers.resolve_id, resolver, 'test')

    def test_resolve_id_multiple(self):
        resolver = lambda r: [12345, 54321]
        self.assertRaises(
            cli.helpers.CLIAbort, cli.helpers.resolve_id, resolver, 'test')


class TestFormatOutput(unittest.TestCase):
    def test_format_output_string(self):
        t = cli.helpers.format_output('just a string', 'raw')
        self.assertEqual('just a string', t)

        t = cli.helpers.format_output(u'just a string', 'raw')
        self.assertEqual(u'just a string', t)

    def test_format_output_raw(self):
        t = cli.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.sortby = 'nothing'
        ret = cli.helpers.format_output(t, 'raw')

        self.assertNotIn('nothing', str(ret))
        self.assertIn('testdata', str(ret))

    def test_format_output_formatted_item(self):
        item = cli.FormattedItem('test', 'test_formatted')
        ret = cli.helpers.format_output(item, 'table')
        self.assertEqual('test_formatted', ret)

    def test_format_output_list(self):
        item = ['this', 'is', 'a', 'list']
        ret = cli.helpers.format_output(item, 'table')
        self.assertEqual(os.linesep.join(item), ret)

    def test_format_output_table(self):
        t = cli.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.sortby = 'nothing'
        ret = cli.helpers.format_output(t, 'table')

        self.assertIn('nothing', str(ret))
        self.assertIn('testdata', str(ret))

    def test_unknown(self):
        t = cli.helpers.format_output({}, 'raw')
        self.assertEqual('{}', t)

    def test_sequentialoutput(self):
        t = cli.helpers.SequentialOutput(blanks=False)
        self.assertTrue(hasattr(t, 'append'))
        t.append('This is a test')
        t.append('')
        t.append('More tests')
        output = cli.helpers.format_output(t)
        self.assertEqual("This is a test\nMore tests", output)

        t.blanks = True
        output = cli.helpers.format_output(t)
        self.assertEqual("This is a test\n\nMore tests", output)
