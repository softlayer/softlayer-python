"""
    SoftLayer.tests.CLI.modules.autoscale_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the autoscale cli command
"""
from SoftLayer import testing


class AutoScaleTests(testing.TestCase):

    def test_autoscale_list(self):
        result = self.run_command(['autoscale', 'list'])
        self.assert_no_fail(result)

    def test_autoscale_detail(self):
        result = self.run_command(['autoscale', 'detail', '12222222'])
        self.assert_no_fail(result)
