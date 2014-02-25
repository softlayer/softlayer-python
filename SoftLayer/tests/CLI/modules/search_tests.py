"""
    SoftLayer.tests.CLI.modules.search_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a series of unit tests and integration tests designed to
    test the given module for the CLI application.

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.tests import unittest, FixtureClient
from mock import Mock, patch, ANY
try:
    # Python 3.x compatibility
    import builtins  # NOQA
    builtins_name = 'builtins'
except ImportError:
    builtins_name = '__builtin__'

from SoftLayer.CLI.helpers import format_output, CLIAbort
from SoftLayer.CLI.modules import search


class SearchCLITests(unittest.TestCase):

    def setUp(self):
        self.client = FixtureClient()

    @patch('SoftLayer.CLI.modules.search.SearchManager.get_search_types')
    def test_search_types(self, get_types_mock):
        expected = [{'Type' : 'vlan'}, {'Type' : 'firewall'}]

        get_types_mock.return_value = [
            'SoftLayer_Network_Vlan',
            'SoftLayer_Network_Vlan_Firewall',
            'SoftLayer_Event_Log'
        ]
        result = search.SearchTypes(client=self.client).execute({})
        self.assertEqual(expected, format_output(result, 'python'))

        get_types_mock.return_value = ['SoftLayer_Network_Vlan', 'SoftLayer_Network_Vlan_Firewall']
        result = search.SearchTypes(client=self.client).execute({})
        self.assertEqual(expected, format_output(result, 'python'))

    @patch('SoftLayer.CLI.modules.search.get_api_type')
    @patch('SoftLayer.CLI.modules.search.SearchManager.get_search_types')
    @patch('SoftLayer.CLI.modules.search.SearchManager.search')
    def test_search_types_args(self, search_mock, get_types_mock, get_api_type_mock):
        args = {
            '-s': 'foo',
            '--types': None
        }

        get_types_mock.return_value = ['SoftLayer_Network_Vlan']
        search_mock.return_value = self.client['Search'].search.return_value

        search.Search(client=self.client).execute(args)
        search_mock.assert_called_with(ANY, ['SoftLayer_Network_Vlan'])

        get_types_mock.return_value = ['SoftLayer_Network_Vlan', 'SoftLayer_Event_Log']
        search.Search(client=self.client).execute(args)
        search_mock.assert_called_with(ANY, ['SoftLayer_Network_Vlan'])

        args['--types'] = 'vlan,ticket'

        get_api_type_mock.return_value = ['SoftLayer_Network_Vlan']

        search.Search(client=self.client).execute(args)
        search_mock.assert_called_with(ANY, [['SoftLayer_Network_Vlan'], ['SoftLayer_Network_Vlan']])

    @patch('SoftLayer.CLI.modules.search.console_input')
    @patch('SoftLayer.CLI.modules.search.SearchManager.get_search_types')
    @patch('SoftLayer.CLI.modules.search.SearchManager.search')
    def test_search_query_arg(self, search_mock, get_types_mock, console_input_mock):
        args = {
            '-s': ' ',
            '--types': None
        }

        get_types_mock.return_value = ['SoftLayer_Network_Vlan']
        search_mock.return_value = self.client['Search'].search.return_value

        search.Search(client=self.client).execute(args)
        search_mock.assert_called_with('*', ANY)

        args['-s'] = 'foo'
        search.Search(client=self.client).execute(args)
        search_mock.assert_called_with('foo', ANY)

        args['-s'] = None
        console_input_mock.return_value = 'bar'
        search.Search(client=self.client).execute(args)
        search_mock.assert_called_with('bar', ANY)

    @patch('SoftLayer.CLI.modules.search.SearchManager.get_search_types')
    @patch('SoftLayer.CLI.modules.search.SearchManager.search')
    def test_search_empty_results(self, search_mock, get_types_mock):
        args = {
            '-s': 'foo',
            '--types': None
        }

        get_types_mock.return_value = ['SoftLayer_Network_Vlan']
        search_mock.return_value = []

        self.assertRaises(CLIAbort, search.Search(client=self.client).execute, args)

    @patch('SoftLayer.CLI.modules.search.SearchManager.get_search_types')
    @patch('SoftLayer.CLI.modules.search.SearchManager.search')
    def test_search_results(self, search_mock, get_types_mock):
        args = {
            '-s': 'foo',
            '--types': None
        }

        get_types_mock.return_value = ['SoftLayer_Network_Vlan']
        search_mock.return_value = [
            {
                'resourceType': 'SoftLayer_Virtual_Guest',
                'relevanceScore': '2.3468237',
                'resource': {
                    'id': 123,
                    'foo': 'app1.example.com'
                },
                'matchedTerms': ['app1', 'app1.example.com']
            }
        ]

        empty_name_expected_row = [{
            'Id' : 123,
            'Type' : 'cci',
            'Name' : None
        }]

        result = search.Search(client=self.client).execute(args)
        self.assertEqual(empty_name_expected_row, format_output(result, 'python'))

        search_mock.return_value = self.client['Search'].search.return_value
        full_expected_rows = [
            {'Id' : 123, 'Type' : 'cci','Name' : ['app1.example.com']},
            {'Id' : 234, 'Type' : 'ip_address','Name' : ['173.192.125.114']},
            {
                'Id' : 345,
                'Type' : 'ticket',
                'Name' : ['MONITORING: Network Monitor Alert A REALLY LONG TITLE FOR ME', '------------']}
        ]

        result = search.Search(client=self.client).execute(args)
        self.assertEqual(full_expected_rows, format_output(result, 'python'))

        raw_expected_rows = [
            {'Id' : 123, 'Type' : 'cci','Name' : 'app1.example.com'},
            {'Id' : 234, 'Type' : 'ip_address','Name' : '173.192.125.114'},
            {
                'Id' : 345,
                'Type' : 'ticket',
                'Name' : 'MONITORING: Network Monitor Alert A REALLY LONG TITLE FOR ME ------------'}
        ]

        args['--raw'] = True

        result = search.Search(client=self.client).execute(args)
        self.assertEqual(raw_expected_rows, format_output(result, 'python'))
