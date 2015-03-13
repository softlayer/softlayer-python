"""
    SoftLayer.tests.CLI.deprecated_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.CLI import deprecated
from SoftLayer import testing


class EnvironmentTests(testing.TestCase):

    def test_main(self):
        try:
            deprecated.main()
        except SystemExit as ex:
            self.assertEquals(ex.code, -1)
