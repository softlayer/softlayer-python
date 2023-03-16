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

    def test_search_instances_basic(self):
        search_string = "TEST_STRING"
        expected = f"_objectType:SoftLayer_Virtual_Guest *{search_string}*"
        self.search.search_instances(search_string)
        self.assert_called_with('SoftLayer_Search', 'advancedSearch',
                                args=(expected,))
        self.search.search_instances(search_string, hostname="thisHostname")
        self.assert_called_with('SoftLayer_Search', 'advancedSearch',
                                args=(f"{expected} hostname: *thisHostname*",))
        self.search.search_instances(search_string, domain="thisDomain")
        self.assert_called_with('SoftLayer_Search', 'advancedSearch',
                                args=(f"{expected} domain: *thisDomain*",))
        self.search.search_instances(search_string, datacenter="dal13")
        self.assert_called_with('SoftLayer_Search', 'advancedSearch',
                                args=(f"{expected} datacenter.longName: *dal13*",))
        self.search.search_instances(search_string, tags=["thisTag"])
        self.assert_called_with('SoftLayer_Search', 'advancedSearch',
                                args=(f"{expected} internalTagReferences.tag.name: thisTag",))
