"""
    SoftLayer.tests.managers.search_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import SearchManager
from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.tests.fixtures import Search

from mock import MagicMock, ANY, call, patch


class SearchTests(unittest.TestCase):

    def setUp(self):
        self.client = FixtureClient()
        self.search = SearchManager(self.client)

    def test_search_missing_types(self):
        self.assertRaises(ValueError, self.search.search, 'abc')

    def test_search_with_default_mask(self):
        expected_ids = [123, 234, 345]
        cci_expected_query = 'abc _objectType:SoftLayer_Virtual_Guest'
        cci_expected_mask = 'mask[resource(SoftLayer_Virtual_Guest)[id,fullyQualifiedDomainName]]'

        results = self.search.search(query='abc', types=['SoftLayer_Virtual_Guest'])
        self.client['Search'].search.assert_called_once_with(
            cci_expected_query, mask=cci_expected_mask
        )
        for result in results:
            self.assertIn(result['resource'].get('id'), expected_ids)

    def test_get_search_types(self):
        expected_names = [
            'SoftLayer_Network_Vlan',
            'SoftLayer_Network_Vlan_Firewall',
            'SoftLayer_Event_Log'
        ]

        results = self.search.get_search_types()
        self.client['Search'].getObjectTypes.assert_called_once()
        for result in results:
            self.assertIn(result, expected_names)
