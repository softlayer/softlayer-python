"""
    SoftLayer.tests.CLI.modules.call_api_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json

from SoftLayer.CLI import call_api
from SoftLayer.CLI import exceptions
from SoftLayer import testing

import pytest


def test_filter_empty():
    assert call_api._build_filters([]) == {}


def test_filter_basic():
    result = call_api._build_filters(['property=value'])
    assert result == {'property': {'operation': '_= value'}}


def test_filter_nested():
    result = call_api._build_filters(['nested.property=value'])
    assert result == {'nested': {'property': {'operation': '_= value'}}}


def test_filter_multi():
    result = call_api._build_filters(['prop1=value1', 'prop2=prop2'])
    assert result == {
        'prop1': {'operation': '_= value1'},
        'prop2': {'operation': '_= prop2'},
    }


def test_filter_in():
    result = call_api._build_filters(['prop IN value1,value2'])
    assert result == {
        'prop': {
            'operation': 'in',
            'options': [{'name': 'data', 'value': ['value1', 'value2']}],
        }
    }


def test_filter_in_multi():
    result = call_api._build_filters([
        'prop_a IN a_val1,a_val2',
        'prop_b IN b_val1,b_val2',
    ])
    assert result == {
        'prop_a': {
            'operation': 'in',
            'options': [{'name': 'data', 'value': ['a_val1', 'a_val2']}],
        },
        'prop_b': {
            'operation': 'in',
            'options': [{'name': 'data', 'value': ['b_val1', 'b_val2']}],
        },
    }


def test_filter_in_with_whitespace():
    result = call_api._build_filters(['prop IN value1 ,  value2  '])
    assert result == {
        'prop': {
            'operation': 'in',
            'options': [{'name': 'data', 'value': ['value1', 'value2']}],
        }
    }


def test_filter_invalid_operation():
    with pytest.raises(exceptions.CLIAbort):
        call_api._build_filters(['prop N/A value1'])


def test_filter_only_whitespace():
    with pytest.raises(exceptions.CLIAbort):
        call_api._build_filters([' '])


class CallCliTests(testing.TestCase):

    def test_python_output(self):
        result = self.run_command(['call-api', 'Service', 'method',
                                   '--mask=some.mask',
                                   '--limit=20',
                                   '--offset=40',
                                   '--id=100',
                                   '-f nested.property=5432',
                                   '--output-python'])

        self.assert_no_fail(result)
        # NOTE(kmcdonald): Python 3 no longer inserts 'u' before unicode
        # string literals but python 2 does. These are stripped out to make
        # this test pass on both python versions.
        stripped_output = result.output.replace("u'", "'")
        self.assertIsNotNone(stripped_output, """import SoftLayer

client = SoftLayer.create_client_from_env()
result = client.call(u'Service',
                     u'method',
                     filter={u'nested': {u'property': {'operation': 5432}}},
                     id=u'100',
                     limit=20,
                     mask=u'some.mask',
                     offset=40)
""")
        self.assertEqual(self.calls(), [], "no API calls were made")

    def test_options(self):
        mock = self.set_mock('SoftLayer_Service', 'method')
        mock.return_value = 'test'

        result = self.run_command(['call-api', 'Service', 'method',
                                   '--mask=some.mask',
                                   '--limit=20',
                                   '--offset=40',
                                   '--id=100',
                                   '-f property=1234',
                                   '-f nested.property=5432'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), 'test')
        self.assert_called_with('SoftLayer_Service', 'method',
                                mask='mask[some.mask]',
                                limit=20,
                                offset=40,
                                identifier='100',
                                filter={
                                    'property': {'operation': 1234},
                                    'nested': {'property': {'operation': 5432}}
                                })

    def test_object(self):
        mock = self.set_mock('SoftLayer_Service', 'method')
        mock.return_value = {'string': 'string',
                             'int': 10,
                             'float': 1.0,
                             'None': None,
                             'Bool': True}

        result = self.run_command(['call-api', 'Service', 'method'])

        self.assert_no_fail(result)
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

        self.assert_no_fail(result)
        # NOTE(kmcdonald): Order is not guaranteed
        self.assertIn(":........:........:", result.output)
        self.assertIn(":   name : value  :", result.output)
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

        self.assert_no_fail(result)
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

        self.assert_no_fail(result)
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

        self.assert_no_fail(result)
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

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Service', 'method',
                                args=('arg1', '1234'))
