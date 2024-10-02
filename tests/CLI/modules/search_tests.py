"""
    SoftLayer.tests.CLI.modules.search_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import testing


class SearchTests(testing.TestCase):

    def test_find(self):
        result = self.run_command(['search', '--types'])
        self.assert_called_with("SoftLayer_Search", "getObjectTypes")
        self.assert_no_fail(result)

    def test_find_advanced(self):
        result = self.run_command(['search', 'hardware', '--advanced'])
        self.assert_called_with("SoftLayer_Search", "advancedSearch", args=('hardware',))
        self.assert_no_fail(result)

    def test_no_options(self):
        result = self.run_command(['search'])
        self.assertEqual(result.exit_code, 2)

    def test_find_single_item(self):
        result = self.run_command(['search', 'test.com'])
        self.assert_no_fail(result)
        self.assert_called_with("SoftLayer_Search", "search", args=('test.com',))
