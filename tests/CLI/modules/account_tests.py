"""
    SoftLayer.tests.CLI.modules.account_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the user cli command
"""
import json
import sys

import mock
import testtools

from SoftLayer import testing


class AccountCLITests(testing.TestCase):

    def test_event_detail(self):
        result = self.run_command(['account', 'event-detail', '1234'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Notification_Occurrence_Event', 'getObject', identifier='1234')