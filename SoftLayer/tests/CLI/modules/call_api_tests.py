"""
    SoftLayer.tests.CLI.modules.call_api_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.CLI import call_api
from SoftLayer.CLI import formatting
from SoftLayer import testing

import json


class CallCliTests(testing.TestCase):

    def test_options(self):
        mock = self.set_mock('SoftLayer_Service', 'method')
        mock.return_value = 'test'

        result = self.run_command(['call-api', 'Service', 'method',
                                   '--mask=some.mask',
                                   '--limit=20',
                                   '--offset=40',
                                   '--id=100'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output), 'test')
        self.assert_called_with('SoftLayer_Service', 'method',
                                mask='mask[some.mask]',
                                limit=20,
                                offset=40,
                                identifier='100')

    def test_object(self):
        mock = self.set_mock('SoftLayer_Service', 'method')
        mock.return_value = {'string': 'string',
                             'int': 10,
                             'float': 1.0,
                             'None': None,
                             'Bool': True}

        result = self.run_command(['call-api', 'Service', 'method'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         {'string': 'string',
                          'int': 10,
                          'float': 1.0,
                          'None': None,
                          'Bool': True})

    def test_object_table(self):
        mock = self.set_mock('SoftLayer_Service', 'method')
        mock.return_value = {'string': 'string',
                             'int': 10,
                             'float': 1.0,
                             'None': None,
                             'Bool': True}

        result = self.run_command(['call-api', 'Service', 'method'],
                                  fmt='table')

        self.assertEqual(result.exit_code, 0)
        # NOTE(kmcdonald): Order is not guaranteed
        self.assertIn(":........:........:", result.output)
        self.assertIn(":   Name : Value  :", result.output)
        self.assertIn(":    int : 10     :", result.output)
        self.assertIn(":   None : None   :", result.output)
        self.assertIn(":  float : 1.0    :", result.output)
        self.assertIn(":   Bool : True   :", result.output)
        self.assertIn(": string : string :", result.output)
        self.assertIn(":........:........:", result.output)

    def test_object_nested(self):
        mock = self.set_mock('SoftLayer_Service', 'method')
        mock.return_value = {'this': {'is': [{'pretty': 'nested'}]}}

        result = self.run_command(['call-api', 'Service', 'method'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         {'this': {'is': [{'pretty': 'nested'}]}})

    def test_list(self):
        mock = self.set_mock('SoftLayer_Service', 'method')
        mock.return_value = [{'string': 'string',
                              'int': 10,
                              'float': 1.0,
                              'None': None,
                              'Bool': True}]

        result = self.run_command(['call-api', 'Service', 'method'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output),
                         [{'string': 'string',
                           'int': 10,
                           'float': 1.0,
                           'None': None,
                           'Bool': True}])

    def test_list_table(self):
        mock = self.set_mock('SoftLayer_Service', 'method')
        mock.return_value = [{'string': 'string',
                              'int': 10,
                              'float': 1.0,
                              'None': None,
                              'Bool': True}]

        result = self.run_command(['call-api', 'Service', 'method'],
                                  fmt='table')

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output,
                         """:......:......:.......:.....:........:
: Bool : None : float : int : string :
:......:......:.......:.....:........:
: True : None :  1.0  :  10 : string :
:......:......:.......:.....:........:
""")

    def test_parameters(self):
        mock = self.set_mock('SoftLayer_Service', 'method')
        mock.return_value = {}

        result = self.run_command(['call-api', 'Service', 'method',
                                   'arg1', '1234'])

        self.assertEqual(result.exit_code, 0)
        self.assert_called_with('SoftLayer_Service', 'method',
                                args=('arg1', '1234'))


class CallCliHelperTests(testing.TestCase):

    def test_format_api_dict(self):
        result = call_api.format_api_dict({'key': 'value'})

        self.assertIsInstance(result, formatting.Table)
        self.assertEqual(result.columns, ['Name', 'Value'])
        self.assertEqual(result.rows, [['key', 'value']])

    def test_format_api_list(self):
        result = call_api.format_api_list([{'key': 'value'}])

        self.assertIsInstance(result, formatting.Table)
        self.assertEqual(result.columns, ['key'])
        self.assertEqual(result.rows, [['value']])

    def test_format_api_list_non_objects(self):
        result = call_api.format_api_list(['a', 'b', 'c'])

        self.assertIsInstance(result, formatting.Table)
        self.assertEqual(result.columns, ['Value'])
        self.assertEqual(result.rows, [['a'], ['b'], ['c']])
