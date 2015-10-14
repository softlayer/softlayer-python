"""
    SoftLayer.tests.basic_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Tests shared code

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing


class TestExceptions(testing.TestCase):

    def test_softlayer_api_error(self):
        e = SoftLayer.SoftLayerAPIError('fault code', 'fault string')
        self.assertEqual(e.faultCode, 'fault code')
        self.assertEqual(e.faultString, 'fault string')
        self.assertEqual(e.reason, 'fault string')
        self.assertEqual(
            repr(e), "<SoftLayerAPIError(fault code): fault string>")
        self.assertEqual(
            str(e), "SoftLayerAPIError(fault code): fault string")

    def test_parse_error(self):
        e = SoftLayer.ParseError('fault code', 'fault string')
        self.assertEqual(e.faultCode, 'fault code')
        self.assertEqual(e.faultString, 'fault string')
        self.assertEqual(e.reason, 'fault string')
        self.assertEqual(
            repr(e), "<ParseError(fault code): fault string>")
        self.assertEqual(
            str(e), "ParseError(fault code): fault string")


class TestUtils(testing.TestCase):

    def test_query_filter(self):
        result = SoftLayer.utils.query_filter('test')
        self.assertEqual({'operation': '_= test'}, result)

        result = SoftLayer.utils.query_filter('~ test')
        self.assertEqual({'operation': '~ test'}, result)

        result = SoftLayer.utils.query_filter('*test')
        self.assertEqual({'operation': '$= test'}, result)

        result = SoftLayer.utils.query_filter('test*')
        self.assertEqual({'operation': '^= test'}, result)

        result = SoftLayer.utils.query_filter('*test*')
        self.assertEqual({'operation': '*= test'}, result)

        result = SoftLayer.utils.query_filter('> 10')
        self.assertEqual({'operation': '> 10'}, result)

        result = SoftLayer.utils.query_filter('>10')
        self.assertEqual({'operation': '> 10'}, result)

        result = SoftLayer.utils.query_filter(10)
        self.assertEqual({'operation': 10}, result)


class TestNestedDict(testing.TestCase):

    def test_basic(self):
        n = SoftLayer.utils.NestedDict()
        self.assertEqual(n['test'], SoftLayer.utils.NestedDict())

        n['test_set'] = 1
        self.assertEqual(n['test_set'], 1)

        d = {
            'test': {
                'nested': 1
            }}

        n = SoftLayer.utils.NestedDict(d)
        self.assertEqual(d, n)
        self.assertEqual(n['test']['nested'], 1)

        # new default top level elements should return a new NestedDict()
        self.assertEqual(n['not']['nested'], SoftLayer.utils.NestedDict())

        # NestedDict doesn't convert dict children, just the top level dict
        # so you can't assume the same behavior with children
        self.assertRaises(KeyError, lambda: n['test']['not']['nested'])

    def test_to_dict(self):
        n = SoftLayer.utils.NestedDict()
        n['test']['test1']['test2']['test3'] = {}
        d = n.to_dict()

        self.assertEqual({
            'test': {'test1': {'test2': {'test3': {}}}}
        }, d)
        self.assertEqual(dict, type(d))
        self.assertEqual(dict, type(d['test']))
        self.assertEqual(dict, type(d['test']['test1']))
        self.assertEqual(dict, type(d['test']['test1']['test2']))
        self.assertEqual(dict, type(d['test']['test1']['test2']['test3']))


class TestLookup(testing.TestCase):

    def test_lookup(self):
        d = {'test': {'nested': 1}}
        val = SoftLayer.utils.lookup(d, 'test')
        self.assertEqual(val, {'nested': 1})

        val = SoftLayer.utils.lookup(d, 'test', 'nested')
        self.assertEqual(val, 1)

        val = SoftLayer.utils.lookup(d, 'test1')
        self.assertEqual(val, None)

        val = SoftLayer.utils.lookup(d, 'test1', 'nested1')
        self.assertEqual(val, None)


def is_a(string):
    if string == 'a':
        return ['this', 'is', 'a']


def is_b(string):
    if string == 'b':
        return ['this', 'is', 'b']


class IdentifierFixture(SoftLayer.utils.IdentifierMixin):
    resolvers = [is_a, is_b]


class TestIdentifierMixin(testing.TestCase):

    def set_up(self):
        self.fixture = IdentifierFixture()

    def test_integer(self):
        ids = self.fixture.resolve_ids(1234)
        self.assertEqual(ids, [1234])

    def test_a(self):
        ids = self.fixture.resolve_ids('a')
        self.assertEqual(ids, ['this', 'is', 'a'])

    def test_b(self):
        ids = self.fixture.resolve_ids('b')
        self.assertEqual(ids, ['this', 'is', 'b'])

    def test_not_found(self):
        ids = self.fixture.resolve_ids('something')
        self.assertEqual(ids, [])

    def test_globalidentifier(self):
        ids = self.fixture.resolve_ids('9d888bc2-7c9a-4dba-bbd8-6bd688687bae')
        self.assertEqual(ids, ['9d888bc2-7c9a-4dba-bbd8-6bd688687bae'])

    def test_globalidentifier_upper(self):
        ids = self.fixture.resolve_ids('B534EF96-55C4-4891-B51A-63866411B58E')
        self.assertEqual(ids, ['B534EF96-55C4-4891-B51A-63866411B58E'])
