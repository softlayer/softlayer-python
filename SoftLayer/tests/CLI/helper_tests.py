"""
    SoftLayer.tests.CLI.helper_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
import sys
import os
import json

import SoftLayer.CLI as cli
from SoftLayer.tests import FIXTURE_PATH, unittest
from mock import patch, mock_open, call


if sys.version_info >= (3,):
    raw_input_path = 'builtins.input'
    open_path = 'builtins.open'
else:
    raw_input_path = '__builtin__.raw_input'
    open_path = '__builtin__.open'


class CLIJSONEncoderTest(unittest.TestCase):
    def test_default(self):
        out = json.dumps({
            'formattedItem': cli.helpers.FormattedItem('normal', 'formatted')
        }, cls=cli.formatting.CLIJSONEncoder)
        self.assertEqual(out, '{"formattedItem": "normal"}')

        out = json.dumps({'normal': 'string'},
                         cls=cli.formatting.CLIJSONEncoder)
        self.assertEqual(out, '{"normal": "string"}')

    def test_fail(self):
        self.assertRaises(
            TypeError,
            json.dumps, {'test': object()}, cls=cli.formatting.CLIJSONEncoder)


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
        runnable = cli.CLIRunnable()
        res = runnable.execute({})
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
        self.assertEqual(None, item.original)
        self.assertEqual('-', item.formatted)
        self.assertEqual('NULL', str(item))


class FormattedListTests(unittest.TestCase):
    def test_init(self):
        l = cli.listing([1, 'two'], separator=':')
        self.assertEqual([1, 'two'], list(l))
        self.assertEqual(':', l.separator)

        l = cli.listing([])
        self.assertEqual(',', l.separator)

    def test_to_python(self):
        l = cli.listing([1, 'two'])
        result = l.to_python()
        self.assertEqual([1, 'two'], result)

        l = cli.listing(x for x in [1, 'two'])
        result = l.to_python()
        self.assertEqual([1, 'two'], result)

    def test_str(self):
        l = cli.listing([1, 'two'])
        result = str(l)
        self.assertEqual('1,two', result)

        l = cli.listing((x for x in [1, 'two']), separator=':')
        result = str(l)
        self.assertEqual('1:two', result)


class CLIAbortTests(unittest.TestCase):

    def test_init(self):
        e = cli.helpers.CLIAbort("something")
        self.assertEqual(2, e.code)
        self.assertEqual("something", e.message)
        self.assertIsInstance(e, cli.helpers.CLIHalt)


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

    def test_format_output_json(self):
        t = cli.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.add_row([cli.helpers.blank()])
        t.sortby = 'nothing'
        ret = cli.helpers.format_output(t, 'json')
        self.assertEqual('''[
    {
        "nothing": "testdata"
    }, 
    {
        "nothing": null
    }
]''', ret)

        ret = cli.helpers.format_output('test', 'json')
        self.assertEqual('"test"', ret)

    def test_format_output_json_keyvaluetable(self):
        t = cli.KeyValueTable(['key', 'value'])
        t.add_row(['nothing', cli.helpers.blank()])
        t.sortby = 'nothing'
        ret = cli.helpers.format_output(t, 'json')
        self.assertEqual('''{
    "nothing": null
}''', ret)

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
        self.assertEqual({}, t)

    def test_sequentialoutput(self):
        t = cli.helpers.SequentialOutput()
        self.assertTrue(hasattr(t, 'append'))
        t.append('This is a test')
        t.append('')
        t.append('More tests')
        output = cli.helpers.format_output(t)
        self.assertEqual("This is a test\nMore tests", output)

        t.separator = ','
        output = cli.helpers.format_output(t)
        self.assertEqual("This is a test,More tests", output)

    def test_format_output_python(self):
        t = cli.helpers.format_output('just a string', 'python')
        self.assertEqual('just a string', t)

        t = cli.helpers.format_output(['just a string'], 'python')
        self.assertEqual(['just a string'], t)

        t = cli.helpers.format_output({'test_key': 'test_value'}, 'python')
        self.assertEqual({'test_key': 'test_value'}, t)

    def test_format_output_python_keyvaluetable(self):
        t = cli.KeyValueTable(['key', 'value'])
        t.add_row(['nothing', cli.helpers.blank()])
        t.sortby = 'nothing'
        ret = cli.helpers.format_output(t, 'python')
        self.assertEqual({'nothing': None}, ret)


class TestTemplateArgs(unittest.TestCase):

    def test_no_template_option(self):
        args = {'key': 'value'}
        cli.helpers.update_with_template_args(args)
        self.assertEqual(args, {'key': 'value'})

    def test_template_not_exists(self):
        path = os.path.join(FIXTURE_PATH, 'sample_template_not_exists.conf')
        self.assertRaises(cli.helpers.ArgumentError,
                          cli.helpers.update_with_template_args,
                          {'--template': path})

    def test_template_options(self):
        path = os.path.join(FIXTURE_PATH, 'sample_cci_template.conf')
        args = {
            'key': 'value',
            '--cpu': None,
            '--memory': '32',
            '--template': path,
            '--hourly': False,
        }
        cli.helpers.update_with_template_args(args)
        self.assertEqual(args, {
            '--cpu': '4',
            '--datacenter': 'dal05',
            '--domain': 'example.com',
            '--hostname': 'myhost',
            '--hourly': 'true',
            '--memory': '32',
            '--monthly': 'false',
            '--network': '100',
            '--os': 'DEBIAN_7_64',
            'key': 'value',
        })


class TestExportToTemplate(unittest.TestCase):
    def test_export_to_template(self):
        with patch(open_path, mock_open(), create=True) as open_:
            cli.helpers.export_to_template('filename', {
                '--os': None,
                '--datacenter': 'ams01',
                '--disk': ['disk1', 'disk2'],
                # The following should get stripped out
                '--config': 'no',
                '--really': 'no',
                '--format': 'no',
                '--debug': 'no',
                # exclude list
                '--test': 'test',
            }, exclude=['--test'])

            open_.assert_called_with('filename', 'w')
            open_().write.assert_has_calls([
                call('datacenter=ams01\n'),
                call('disk=disk1,disk2\n'),
            ], any_order=True)  # Order isn't really guaranteed
