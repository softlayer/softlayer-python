"""
    SoftLayer.tests.CLI.helper_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import os
import sys

import mock

from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import template
from SoftLayer import testing

if sys.version_info >= (3,):
    open_path = 'builtins.open'
else:
    open_path = '__builtin__.open'


class CLIJSONEncoderTest(testing.TestCase):
    def test_default(self):
        out = json.dumps({
            'formattedItem': formatting.FormattedItem('normal', 'formatted')
        }, cls=formatting.CLIJSONEncoder)
        self.assertEqual(out, '{"formattedItem": "normal"}')

        out = json.dumps({'normal': 'string'},
                         cls=formatting.CLIJSONEncoder)
        self.assertEqual(out, '{"normal": "string"}')

    def test_fail(self):
        self.assertRaises(
            TypeError,
            json.dumps, {'test': object()}, cls=formatting.CLIJSONEncoder)


class PromptTests(testing.TestCase):

    @mock.patch('click.prompt')
    def test_invalid_response(self, prompt_mock):
        prompt_mock.return_value = 'y'
        result = formatting.valid_response('test', 'n')
        prompt_mock.assert_called_with('test')
        self.assertFalse(result)

        prompt_mock.return_value = 'wakakwakwaka'
        result = formatting.valid_response('test', 'n')
        prompt_mock.assert_called_with('test')
        self.assertFalse(result)

        prompt_mock.return_value = ''
        result = formatting.valid_response('test', 'n')
        prompt_mock.assert_called_with('test')
        self.assertEqual(result, None)

    @mock.patch('click.prompt')
    def test_valid_response(self, prompt_mock):
        prompt_mock.return_value = 'n'
        result = formatting.valid_response('test', 'n')
        prompt_mock.assert_called_with('test')
        self.assertTrue(result)

        prompt_mock.return_value = 'N'
        result = formatting.valid_response('test', 'n')
        prompt_mock.assert_called_with('test')
        self.assertTrue(result)

    @mock.patch('click.prompt')
    def test_do_or_die(self, prompt_mock):
        confirmed = '37347373737'
        prompt_mock.return_value = confirmed
        result = formatting.no_going_back(confirmed)
        self.assertTrue(result)

        # no_going_back should cast int's to str()
        confirmed = '4712309182309'
        prompt_mock.return_value = confirmed
        result = formatting.no_going_back(int(confirmed))
        self.assertTrue(result)

        confirmed = None
        prompt_mock.return_value = ''
        result = formatting.no_going_back(confirmed)
        self.assertFalse(result)

    @mock.patch('click.prompt')
    def test_confirmation(self, prompt_mock):
        prompt_mock.return_value = 'Y'
        res = formatting.confirm('Confirm?', default=False)
        self.assertTrue(res)

        prompt_mock.return_value = 'N'
        res = formatting.confirm('Confirm?', default=False)
        self.assertFalse(res)

        prompt_mock.return_value = ''
        res = formatting.confirm('Confirm?', default=True)
        self.assertTrue(res)


class FormattedItemTests(testing.TestCase):

    def test_init(self):
        item = formatting.FormattedItem('test', 'test_formatted')
        self.assertEqual('test', item.original)
        self.assertEqual('test_formatted', item.formatted)
        self.assertEqual('test', str(item))

        item = formatting.FormattedItem('test')
        self.assertEqual('test', item.original)
        self.assertEqual('test', item.formatted)
        self.assertEqual('test', str(item))

    def test_mb_to_gb(self):
        item = formatting.mb_to_gb(1024)
        self.assertEqual(1024, item.original)
        self.assertEqual('1G', item.formatted)

        item = formatting.mb_to_gb('1024')
        self.assertEqual('1024', item.original)
        self.assertEqual('1G', item.formatted)

        item = formatting.mb_to_gb('1025.0')
        self.assertEqual('1025.0', item.original)
        self.assertEqual('1G', item.formatted)

        self.assertRaises(ValueError, formatting.mb_to_gb, '1024string')

    def test_gb(self):
        item = formatting.gb(2)
        self.assertEqual(2048, item.original)
        self.assertEqual('2G', item.formatted)

        item = formatting.gb('2')
        self.assertEqual(2048, item.original)
        self.assertEqual('2G', item.formatted)

        item = formatting.gb('2.0')
        self.assertEqual(2048, item.original)
        self.assertEqual('2G', item.formatted)

    def test_blank(self):
        item = formatting.blank()
        self.assertEqual(None, item.original)
        self.assertEqual('-', item.formatted)
        self.assertEqual('NULL', str(item))


class FormattedListTests(testing.TestCase):
    def test_init(self):
        l = formatting.listing([1, 'two'], separator=':')
        self.assertEqual([1, 'two'], list(l))
        self.assertEqual(':', l.separator)

        l = formatting.listing([])
        self.assertEqual(',', l.separator)

    def test_to_python(self):
        l = formatting.listing([1, 'two'])
        result = l.to_python()
        self.assertEqual([1, 'two'], result)

        l = formatting.listing(x for x in [1, 'two'])
        result = l.to_python()
        self.assertEqual([1, 'two'], result)

    def test_str(self):
        l = formatting.listing([1, 'two'])
        result = str(l)
        self.assertEqual('1,two', result)

        l = formatting.listing((x for x in [1, 'two']), separator=':')
        result = str(l)
        self.assertEqual('1:two', result)


class FormattedTxnTests(testing.TestCase):
    def test_active_txn_empty(self):
        self.assertRaises(KeyError, formatting.active_txn, {})

    def test_active_txn(self):
        result = formatting.active_txn({
            'activeTransaction': {
                'transactionStatus': {
                    'name': 'a',
                    'friendlyName': 'b'
                }
            }
        })
        self.assertEqual(result.original, 'a')
        self.assertEqual(result.formatted, 'b')
        self.assertIsInstance(result, formatting.FormattedItem)

    def test_active_txn_missing(self):
        # A dict with activeTransaction but not transactionStatus
        # should return blank() instead of raising an exception

        b = formatting.blank()

        result = formatting.active_txn({
            'activeTransaction': {}
        })
        self.assertIsInstance(result, formatting.FormattedItem)
        self.assertEqual(result.original, b.original)

    def test_transaction_status(self):
        result = formatting.transaction_status({
            'transactionStatus': {
                'name': 'a',
                'friendlyName': 'b'
            }
        })
        self.assertEqual(result.original, 'a')
        self.assertEqual(result.formatted, 'b')
        self.assertIsInstance(result, formatting.FormattedItem)

    def test_transaction_status_missing(self):
        b = formatting.blank()

        result = formatting.transaction_status({
            'transactionStatus': {}
        })
        self.assertIsInstance(result, formatting.FormattedItem)
        self.assertEqual(result.original, b.original)


class CLIAbortTests(testing.TestCase):

    def test_init(self):
        e = exceptions.CLIAbort("something")
        self.assertEqual(2, e.code)
        self.assertEqual("something", e.message)
        self.assertIsInstance(e, exceptions.CLIHalt)


class ResolveIdTests(testing.TestCase):

    def test_resolve_id_one(self):
        resolver = lambda r: [12345]
        id = helpers.resolve_id(resolver, 'test')
        self.assertEqual(id, 12345)

    def test_resolve_id_none(self):
        resolver = lambda r: []
        self.assertRaises(
            exceptions.CLIAbort, helpers.resolve_id, resolver, 'test')

    def test_resolve_id_multiple(self):
        resolver = lambda r: [12345, 54321]
        self.assertRaises(
            exceptions.CLIAbort, helpers.resolve_id, resolver, 'test')


class TestFormatOutput(testing.TestCase):

    def test_format_output_string(self):
        t = formatting.format_output('just a string', 'raw')
        self.assertEqual('just a string', t)

        t = formatting.format_output(b'just a string', 'raw')
        self.assertEqual(b'just a string', t)

    def test_format_output_raw(self):
        t = formatting.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.sortby = 'nothing'
        ret = formatting.format_output(t, 'raw')

        self.assertNotIn('nothing', str(ret))
        self.assertIn('testdata', str(ret))

    def test_format_output_json(self):
        t = formatting.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.add_row([formatting.blank()])
        t.sortby = 'nothing'
        ret = formatting.format_output(t, 'json')
        # This uses json.dumps due to slight changes in the output between
        # py3.3 and py3.4
        expected = json.dumps([{'nothing': 'testdata'}, {'nothing': None}],
                              indent=4)
        self.assertEqual(expected, ret)

        ret = formatting.format_output('test', 'json')
        self.assertEqual('"test"', ret)

    def test_format_output_json_keyvaluetable(self):
        t = formatting.KeyValueTable(['key', 'value'])
        t.add_row(['nothing', formatting.blank()])
        t.sortby = 'nothing'
        ret = formatting.format_output(t, 'json')
        self.assertEqual('''{
    "nothing": null
}''', ret)

    def test_format_output_formatted_item(self):
        item = formatting.FormattedItem('test', 'test_formatted')
        ret = formatting.format_output(item, 'table')
        self.assertEqual('test_formatted', ret)

    def test_format_output_list(self):
        item = ['this', 'is', 'a', 'list']
        ret = formatting.format_output(item, 'table')
        self.assertEqual(os.linesep.join(item), ret)

    def test_format_output_table(self):
        t = formatting.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.sortby = 'nothing'
        ret = formatting.format_output(t, 'table')

        self.assertIn('nothing', str(ret))
        self.assertIn('testdata', str(ret))

    def test_unknown(self):
        t = formatting.format_output({}, 'raw')
        self.assertEqual({}, t)

    def test_sequentialoutput(self):
        t = formatting.SequentialOutput()
        self.assertTrue(hasattr(t, 'append'))
        t.append('This is a test')
        t.append('')
        t.append('More tests')
        output = formatting.format_output(t)
        self.assertEqual("This is a test\nMore tests", output)

        t.separator = ','
        output = formatting.format_output(t)
        self.assertEqual("This is a test,More tests", output)

    def test_format_output_python(self):
        t = formatting.format_output('just a string', 'python')
        self.assertEqual('just a string', t)

        t = formatting.format_output(['just a string'], 'python')
        self.assertEqual(['just a string'], t)

        t = formatting.format_output({'test_key': 'test_value'}, 'python')
        self.assertEqual({'test_key': 'test_value'}, t)

    def test_format_output_python_keyvaluetable(self):
        t = formatting.KeyValueTable(['key', 'value'])
        t.add_row(['nothing', formatting.blank()])
        t.sortby = 'nothing'
        ret = formatting.format_output(t, 'python')
        self.assertEqual({'nothing': None}, ret)


class TestTemplateArgs(testing.TestCase):

    def test_no_template_option(self):
        args = {'key': 'value'}
        template.update_with_template_args(args)
        self.assertEqual(args, {'key': 'value'})

    def test_template_options(self):
        path = os.path.join(testing.FIXTURE_PATH, 'sample_vs_template.conf')
        args = {
            'cpu': None,
            'memory': '32',
            'template': path,
            'hourly': False,
            'disk': [],
        }
        template.update_with_template_args(args, list_args=['disk'])
        self.assertEqual(args, {
            'cpu': '4',
            'datacenter': 'dal05',
            'domain': 'example.com',
            'hostname': 'myhost',
            'hourly': 'true',
            'memory': '32',
            'monthly': 'false',
            'network': '100',
            'os': 'DEBIAN_7_64',
            'disk': ['50', '100'],
        })


class TestExportToTemplate(testing.TestCase):
    def test_export_to_template(self):
        with mock.patch(open_path, mock.mock_open(), create=True) as open_:
            template.export_to_template('filename', {
                'os': None,
                'datacenter': 'ams01',
                'disk': ('disk1', 'disk2'),
                # The following should get stripped out
                'config': 'no',
                'really': 'no',
                'format': 'no',
                'debug': 'no',
                # exclude list
                'test': 'test',
            }, exclude=['test'])

            open_.assert_called_with('filename', 'w')
            open_().write.assert_has_calls([
                mock.call('datacenter=ams01\n'),
                mock.call('disk=disk1,disk2\n'),
            ], any_order=True)  # Order isn't really guaranteed
