"""
    SoftLayer.tests.CLI.modules.autoscale_tests
<<<<<<< HEAD
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
=======
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
>>>>>>> 63de0adb45c6c1ccc7135520ebcdaeb38249e9fa
"""
from SoftLayer import testing


<<<<<<< HEAD
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

    def test_scale_ca(self):
        result = self.run_command(['autoscale', 'scale', '789654123', '--by', '--down', '--amount', '1'])
=======
class AutoScaleTests(testing.TestCase):

    def test_autoscale_list(self):
        result = self.run_command(['autoscale', 'list'])
>>>>>>> 63de0adb45c6c1ccc7135520ebcdaeb38249e9fa
        self.assert_no_fail(result)
