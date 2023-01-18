"""
    SoftLayer.tests.CLI.modules.find_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import testing


class FindTests(testing.TestCase):

    def test_find(self):
        result = self.run_command(['search', '--types'])
        self.assert_no_fail(result)

    def test_find_advanced(self):
        result = self.run_command(['search', 'hardware', '--advanced'])
        self.assert_no_fail(result)
