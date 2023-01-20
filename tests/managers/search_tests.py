"""
    SoftLayer.tests.managers.search_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.managers.search import SearchManager
from SoftLayer import testing


class SearchTests(testing.TestCase):

    def set_up(self):
        self.search = SearchManager(self.client)

    def test_search_type(self):
        self.search.get_object_types()
        self.assert_called_with('SoftLayer_Search', 'getObjectTypes')

    def test_search(self):
        self.search.search('SoftLayer_Hardware')
        self.assert_called_with('SoftLayer_Search', 'search')

    def test_search_advanced(self):
        self.search.advanced('SoftLayer_Hardware')
        self.assert_called_with('SoftLayer_Search', 'advancedSearch')
