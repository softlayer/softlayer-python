# -*- coding: utf-8 -*-
"""
    SoftLayer.tests.CLI.helper_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import os
import sys
import tempfile

import click
from unittest import mock as mock

from SoftLayer.CLI import core
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import template
from SoftLayer import testing


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

        prompt_mock.return_value = 'Y'
        res = formatting.confirm('Confirm?', default=True)
        self.assertTrue(res)
        prompt_mock.assert_called_with('Confirm? [Y/n]',
                                       default='y',
                                       show_default=False)

        prompt_mock.return_value = 'N'
        res = formatting.confirm('Confirm?', default=False)
        self.assertFalse(res)
        prompt_mock.assert_called_with('Confirm? [y/N]',
                                       default='n',
                                       show_default=False)


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

    def test_sort_mixed(self):
        blank = formatting.blank()
        items = [10, blank]
        sorted_items = sorted(items)
        self.assertEqual(sorted_items, [blank, 10])

        items = [blank, 10]
        sorted_items = sorted(items)
        self.assertEqual(sorted_items, [blank, 10])

        items = [blank, "10"]
        sorted_items = sorted(items)
        self.assertEqual(sorted_items, [blank, "10"])

    def test_sort(self):
        items = [10, formatting.FormattedItem(20), formatting.FormattedItem(5)]
        sorted_items = sorted(items)
        self.assertEqual(sorted_items, [formatting.FormattedItem(5),
                                        10,
                                        formatting.FormattedItem(20)])


class FormattedListTests(testing.TestCase):
    def test_init(self):
        listing = formatting.listing([1, 'two'], separator=':')
        self.assertEqual([1, 'two'], list(listing))
        self.assertEqual(':', listing.separator)

        listing = formatting.listing([])
        self.assertEqual(',', listing.separator)

    def test_to_python(self):
        listing = formatting.listing([1, 'two'])
        result = listing.to_python()
        self.assertEqual([1, 'two'], result)

        listing = formatting.listing(x for x in [1, 'two'])
        result = listing.to_python()
        self.assertEqual([1, 'two'], result)

    def test_str(self):
        listing = formatting.listing([1, 'two'])
        result = str(listing)
        self.assertEqual('1,two', result)

        listing = formatting.listing((x for x in [1, 'two']), separator=':')
        result = str(listing)
        self.assertEqual('1:two', result)


class FormattedTxnTests(testing.TestCase):
    def test_active_txn_empty(self):
        result = formatting.active_txn({})
        self.assertEqual(str(result), 'NULL')

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
        self.assertEqual(helpers.resolve_id(lambda r: [12345], 'test'), 12345)

    def test_resolve_id_none(self):
        self.assertRaises(
            exceptions.CLIAbort, helpers.resolve_id, lambda r: [], 'test')

    def test_resolve_id_multiple(self):
        self.assertRaises(
            exceptions.CLIAbort, helpers.resolve_id, lambda r: [12345, 54321], 'test')


class TestTable(testing.TestCase):

    def test_table_with_duplicated_columns(self):
        self.assertRaises(exceptions.CLIHalt, formatting.Table, ['col', 'col'])


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

    def test_format_output_jsonraw(self):
        t = formatting.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.add_row([formatting.blank()])
        t.sortby = 'nothing'
        ret = formatting.format_output(t, 'jsonraw')
        # This uses json.dumps due to slight changes in the output between
        # py3.3 and py3.4
        expected = json.dumps([{'nothing': 'testdata'}, {'nothing': None}])
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

    def test_format_output_jsonraw_keyvaluetable(self):
        t = formatting.KeyValueTable(['key', 'value'])
        t.add_row(['nothing', formatting.blank()])
        t.sortby = 'nothing'
        ret = formatting.format_output(t, 'jsonraw')
        self.assertEqual('''{"nothing": null}''', ret)

    def test_format_output_json_string(self):
        ret = formatting.format_output("test", 'json')
        self.assertEqual('"test"', ret)

    def test_format_output_jsonraw_string(self):
        ret = formatting.format_output("test", 'jsonraw')
        self.assertEqual('"test"', ret)

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
        # specifying the separator prevents windows from using \n\r
        t = formatting.SequentialOutput(separator="\n")
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

    def test_format_output_unicode(self):
        t = formatting.format_output('☃', 'raw')
        self.assertEqual('☃', t)

        item = formatting.FormattedItem('raw ☃', '☃')
        t = formatting.format_output(item)
        self.assertEqual('☃', t)

        t = formatting.format_output(item, 'raw')
        self.assertEqual('raw ☃', t)

    def test_format_output_table_invalid_sort(self):
        t = formatting.Table(['nothing'])
        t.align['nothing'] = 'c'
        t.add_row(['testdata'])
        t.sortby = 'DOES NOT EXIST'
        self.assertRaises(
            exceptions.CLIHalt,
            formatting.format_output, t, 'table',
        )


class TestTemplateArgs(testing.TestCase):

    def test_no_template_option(self):
        ctx = click.Context(core.cli)
        template.TemplateCallback()(ctx, None, None)
        self.assertIsNone(ctx.default_map)

    def test_template_options(self):
        ctx = click.Context(core.cli)
        path = os.path.join(testing.FIXTURE_PATH, 'sample_vs_template.conf')
        template.TemplateCallback(list_args=['disk'])(ctx, None, path)
        self.assertEqual(ctx.default_map, {
            'cpu': '4',
            'datacenter': 'dal05',
            'domain': 'example.com',
            'hostname': 'myhost',
            'hourly': 'true',
            'memory': '1024',
            'monthly': 'false',
            'network': '100',
            'os': 'DEBIAN_7_64',
            'disk': ['50', '100'],
        })


class TestExportToTemplate(testing.TestCase):

    def test_export_to_template(self):
        if (sys.platform.startswith("win")):
            self.skipTest("Test doesn't work in Windows")
        # Tempfile creation is wonky on windows
        with tempfile.NamedTemporaryFile() as tmp:
            template.export_to_template(tmp.name, {
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

            with open(tmp.name) as f:
                data = f.read()

                self.assertEqual(len(data.splitlines()), 2)
                self.assertIn('datacenter=ams01\n', data)
                self.assertIn('disk=disk1,disk2\n', data)


class IterToTableTests(testing.TestCase):

    def test_format_api_dict(self):
        result = formatting._format_dict({'key': 'value'})

        self.assertIsInstance(result, formatting.Table)
        self.assertEqual(result.columns, ['name', 'value'])
        self.assertEqual(result.rows, [['key', 'value']])

    def test_format_api_list(self):
        result = formatting._format_list([{'key': 'value'}])

        self.assertIsInstance(result, formatting.Table)
        self.assertEqual(result.columns, ['key'])
        self.assertEqual(result.rows, [['value']])

    def test_format_api_list_non_objects(self):
        result = formatting._format_list(['a', 'b', 'c'])

        self.assertIsInstance(result, formatting.Table)
        self.assertEqual(result.columns, ['value'])
        self.assertEqual(result.rows, [['a'], ['b'], ['c']])

    def test_format_api_list_with_none_value(self):
        result = formatting._format_list([{'key': [None, 'value']}, None])

        self.assertIsInstance(result, formatting.Table)
        self.assertEqual(result.columns, ['key'])
