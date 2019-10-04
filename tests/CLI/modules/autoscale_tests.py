"""
    SoftLayer.tests.CLI.modules.autoscale_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the autoscale cli command
"""
from SoftLayer import testing


class AutoscaleTests(testing.TestCase):

    def test_logs_dates(self):
        result = self.run_command(['autoscale', 'logs', '123456', '-d', '2019-02-02'])
        print(result)
        self.assert_no_fail(result)

    def test_scale_down(self):
        result = self.run_command(['autoscale', 'scale', '123456', '--down', '--amount', '2'])
        self.assert_no_fail(result)

    def test_scale_up(self):
        result = self.run_command(['autoscale', 'scale', '123456', '--up', '--amount', '2'])
        self.assert_no_fail(result)

    def test_scale_to(self):
        result = self.run_command(['autoscale', 'scale', '789654123', '--down', '--amount', '2'])
        self.assert_no_fail(result)

    def test_scale_by_up(self):
        result = self.run_command(['autoscale', 'scale', '789654123', '--by', '--down', '--amount', '-1'])
        self.assert_no_fail(result)

    def test_scale_cancel(self):
        result = self.run_command(['autoscale', 'scale', '789654123', '--by', '--down', '--amount', '1'])
        self.assert_no_fail(result)

    def test_autoscale_list(self):
        result = self.run_command(['autoscale', 'list'])
        self.assert_no_fail(result)

    def test_autoscale_detail(self):
        result = self.run_command(['autoscale', 'detail', '12222222'])
        self.assert_no_fail(result)

    def test_autoscale_tag(self):
        result = self.run_command(['autoscale', 'tag', '12345'])
        self.assert_no_fail(result)

    def test_autoscale_edit(self):
        result = self.run_command(['autoscale', 'edit', '12345'])
        self.assert_no_fail(result)
