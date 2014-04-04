"""
    SoftLayer.tests.managers.cci_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import CCIManager
from SoftLayer.tests import unittest, FixtureClient

from mock import ANY, call


class CCITests(unittest.TestCase):
    """
    Small class to verify the rename of CCIManager to VSManager didn't
    break any existing code.
    """
    def setUp(self):
        self.client = FixtureClient()
        self.cci = CCIManager(self.client)

    def test_list_instances(self):
        mcall = call(mask=ANY, filter={})
        service = self.client['Account']

        list_expected_ids = [100, 104]
        hourly_expected_ids = [104]
        monthly_expected_ids = [100]

        results = self.cci.list_instances(hourly=True, monthly=True)
        service.getVirtualGuests.assert_has_calls(mcall)
        for result in results:
            self.assertIn(result['id'], list_expected_ids)

        result = self.cci.list_instances(hourly=False, monthly=False)
        service.getVirtualGuests.assert_has_calls(mcall)
        for result in results:
            self.assertIn(result['id'], list_expected_ids)

        results = self.cci.list_instances(hourly=False, monthly=True)
        service.getMonthlyVirtualGuests.assert_has_calls(mcall)
        for result in results:
            self.assertIn(result['id'], monthly_expected_ids)

        results = self.cci.list_instances(hourly=True, monthly=False)
        service.getHourlyVirtualGuests.assert_has_calls(mcall)
        for result in results:
            self.assertIn(result['id'], hourly_expected_ids)
