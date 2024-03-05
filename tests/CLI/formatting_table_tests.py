"""
    SoftLayer.tests.CLI.formatting_table_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer import testing


class TestTable(testing.TestCase):

    def test_table_with_duplicated_columns(self):
        self.assertRaises(exceptions.CLIHalt, formatting.Table, ['col', 'col'])

    def test_boolean_table(self):
        table = formatting.Table(["column1"], title="Test Title")
        self.assertFalse(table)
        table.add_row(["entry1"])
        self.assertTrue(table)


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

    def test_format_api_list_with_empty_array(self):
        result = formatting.iter_to_table([{'id': 130224450, 'activeTickets': []}])
        self.assertIsInstance(result, formatting.Table)
        self.assertIn('id', result.columns)
        self.assertIn('activeTickets', result.columns)
        formatted = formatting.format_output(result, "table")
        # No good ways to test whats actually in a Rich.Table without going through the hassel of
        # printing it out. As long as this didn't throw and exception it should be fine.
        self.assertEqual(formatted.row_count, 1)
