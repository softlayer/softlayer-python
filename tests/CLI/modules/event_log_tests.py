"""
    SoftLayer.tests.CLI.modules.event_log_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :license: MIT, see LICENSE for more details.
"""

import json

from SoftLayer import SoftLayerAPIError
from SoftLayer import testing


class EventLogTests(testing.TestCase):

    def test_get_event_log_with_metadata(self):
        result = self.run_command(['event-log', 'get', '--metadata'])

        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects')
        self.assertIn('Metadata', result.output)

    def test_get_event_log_without_metadata(self):
        result = self.run_command(['event-log', 'get', '--no-metadata'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects')
        self.assert_called_with('SoftLayer_User_Customer', 'getObject', identifier=400)
        self.assertNotIn('Metadata', result.output)

    def test_get_event_log_empty(self):
        mock = self.set_mock('SoftLayer_Event_Log', 'getAllObjects')
        mock.return_value = None

        result = self.run_command(['event-log', 'get'])

        self.assert_no_fail(result)
        self.assertIn("No logs available for filter ", result.output)

    def test_get_event_log_over_limit(self):
        result = self.run_command(['event-log', 'get', '-l 1'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects')
        self.assertEqual(2, result.output.count("\n"))

    def test_get_event_log_types(self):
        expected = [
            {
                "types": {"value": "Account"}
            },
            {
                "types": {"value": "CDN"}
            },
            {
                "types": {"value": "User"}
            },
            {
                "types": {"value": "Bare Metal Instance"}
            },
            {
                "types": {"value": "API Authentication"}
            },
            {
                "types": {"value": "Server"}
            },
            {
                "types": {"value": "CCI"}
            },
            {
                "types": {"value": "Image"}
            },
            {
                "types": {"value": "Bluemix LB"}
            },
            {
                "types": {"value": "Facility"}
            },
            {
                "types": {"value": "Cloud Object Storage"}
            },
            {
                "types": {"value": "Security Group"}
            }
        ]

        result = self.run_command(['event-log', 'types'])

        self.assert_no_fail(result)
        self.assertEqual(expected, json.loads(result.output))

    def test_get_unlimited_events(self):
        result = self.run_command(['event-log', 'get', '-l -1'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects')
        self.assertEqual(8, result.output.count("\n"))

    def test_issues1905(self):
        """https://github.com/softlayer/softlayer-python/issues/1905"""
        getUser = self.set_mock('SoftLayer_User_Customer', 'getObject')
        getUser.side_effect = SoftLayerAPIError(
            "SoftLayer_Exception_PermissionDenied",
            "You do not have permission to access this user")
        result = self.run_command(['event-log', 'get', '-l -1'])
        self.assert_no_fail(result)
        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects')
        self.assert_called_with('SoftLayer_User_Customer', 'getObject', identifier=400)
        user_calls = self.calls('SoftLayer_User_Customer', 'getObject')
        self.assertEqual(1, len(user_calls))
