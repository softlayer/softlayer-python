"""
    SoftLayer.tests.utils_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Tests shared code

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing
from SoftLayer import utils


TEST_FILTER = {
    'virtualGuests': {
        'provisionDate': {
            'operation': 'orderBy',
            'options': [
                {'name': 'sort', 'value': ['DESC']},
                {'name': 'sortOrder', 'value': [1]}
            ]
        },
        'maxMemory': {
            'operation': 'orderBy',
            'options': [
                {'name': 'sort', 'value': ['ASC']},
                {'name': 'sortOrder', 'value': [0]}
            ]
        },
    },
    'hardware': {
        'sparePoolBillingItem': {
            'id': {'operation': 'not null'}
        }
    },
    'someProperty': {
        'provisionDate': {
            'operation': '> sysdate - 30'
        }
    }
}


class TestUtils(testing.TestCase):

    def test_find_key_simple(self):
        """Simple test case"""
        test_dict = {"key1": "value1", "nested": {"key2": "value2", "key3": "value4"}}
        result = utils.has_key_value(test_dict, "key2", "value2")
        self.assertIsNotNone(result)
        self.assertTrue(result)

    def test_find_object_filter(self):
        """Find first orderBy operation in a real-ish object filter"""

        result = utils.has_key_value(TEST_FILTER)
        self.assertIsNotNone(result)
        self.assertTrue(result)

    def test_not_found(self):
        """Nothing to be found"""
        test_dict = {"key1": "value1", "nested": {"key2": "value2", "key3": "value4"}}
        result = utils.has_key_value(test_dict, "key23", "value2")
        self.assertFalse(result)

    def test_fix_filter(self):
        original_filter = {}
        fixed_filter = utils.fix_filter(original_filter)
        self.assertIsNotNone(fixed_filter)
        self.assertEqual(fixed_filter.get('id'), utils.query_filter_orderby())
        # testing to make sure original doesn't get changed by the function call
        self.assertIsNone(original_filter.get('id'))

    def test_billing_filter(self):
        billing_filter = {
            'allTopLevelBillingItems': {
                'cancellationDate': {'operation': 'is null'},
                'id': {'operation': 'orderBy', 'options': [{'name': 'sort', 'value': ['ASC']}]}
            }
        }

        fixed_filter = utils.fix_filter(billing_filter)
        # Make sure we didn't add any more items
        self.assertEqual(len(fixed_filter), 1)
        self.assertEqual(len(fixed_filter.get('allTopLevelBillingItems')), 2)
        self.assertDictEqual(fixed_filter, billing_filter)
