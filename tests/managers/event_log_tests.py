"""
    SoftLayer.tests.managers.event_log_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import fixtures
from SoftLayer import testing


class EventLogTests(testing.TestCase):

    def set_up(self):
        self.event_log = SoftLayer.EventLogManager(self.client)

    def test_get_event_logs(self):
        result = self.event_log.get_event_logs(None)

        expected = fixtures.SoftLayer_Event_Log.getAllObjects
        self.assertEqual(expected, result)

    def test_get_event_log_types(self):
        result = self.event_log.get_event_log_types()

        expected = fixtures.SoftLayer_Event_Log.getAllEventObjectNames
        self.assertEqual(expected, result)

    def test_get_event_logs_by_type(self):
        expected = [
            {
                'accountId': 100,
                'eventCreateDate': '2017-10-23T14:22:36.221541-05:00',
                'eventName': 'Disable Port',
                'ipAddress': '192.168.0.1',
                'label': 'test.softlayer.com',
                'metaData': '',
                'objectId': 300,
                'objectName': 'CCI',
                'traceId': '100',
                'userId': '',
                'userType': 'SYSTEM'
            }
        ]

        mock = self.set_mock('SoftLayer_Event_Log', 'getAllObjects')
        mock.return_value = expected

        result = self.event_log.get_event_logs_by_type('CCI')

        self.assertEqual(expected, result)

    def test_get_event_logs_by_event_name(self):
        expected = [
            {
                'accountId': 100,
                'eventCreateDate': '2017-10-18T09:40:32.238869-05:00',
                'eventName': 'Security Group Added',
                'ipAddress': '192.168.0.1',
                'label': 'test.softlayer.com',
                'metaData': '{"securityGroupId":"200",'
                            '"securityGroupName":"test_SG",'
                            '"networkComponentId":"100",'
                            '"networkInterfaceType":"public",'
                            '"requestId":"96c9b47b9e102d2e1d81fba"}',
                'objectId': 300,
                'objectName': 'CCI',
                'traceId': '59e767e03a57e',
                'userId': 400,
                'userType': 'CUSTOMER',
                'username': 'user'
            }
        ]

        mock = self.set_mock('SoftLayer_Event_Log', 'getAllObjects')
        mock.return_value = expected

        result = self.event_log.get_event_logs_by_event_name('Security Group Added')

        self.assertEqual(expected, result)

    def test_build_filter_no_args(self):
        result = self.event_log.build_filter(None, None, None, None, None, None)

        self.assertEqual(result, None)

    def test_build_filter_min_date(self):
        expected = {
            'eventCreateDate': {
                'operation': 'greaterThanDate',
                'options': [
                    {
                        'name': 'date',
                        'value': [
                            '2017-10-30T00:00:00.000000+00:00'
                        ]
                    }
                ]
            }
        }

        result = self.event_log.build_filter('10/30/2017', None, None, None, None, None)

        self.assertEqual(expected, result)

    def test_build_filter_max_date(self):
        expected = {
            'eventCreateDate': {
                'operation': 'lessThanDate',
                'options': [
                    {
                        'name': 'date',
                        'value': [
                            '2017-10-31T00:00:00.000000+00:00'
                        ]
                    }
                ]
            }
        }

        result = self.event_log.build_filter(None, '10/31/2017', None, None, None, None)

        self.assertEqual(expected, result)

    def test_build_filter_min_max_date(self):
        expected = {
            'eventCreateDate': {
                'operation': 'betweenDate',
                'options': [
                    {
                        'name': 'startDate',
                        'value': [
                            '2017-10-30T00:00:00.000000+00:00'
                        ]
                    },
                    {
                        'name': 'endDate',
                        'value': [
                            '2017-10-31T00:00:00.000000+00:00'
                        ]
                    }
                ]
            }
        }

        result = self.event_log.build_filter('10/30/2017', '10/31/2017', None, None, None, None)

        self.assertEqual(expected, result)

    def test_build_filter_min_date_pos_utc(self):
        expected = {
            'eventCreateDate': {
                'operation': 'greaterThanDate',
                'options': [
                    {
                        'name': 'date',
                        'value': [
                            '2017-10-30T00:00:00.000000+05:00'
                        ]
                    }
                ]
            }
        }

        result = self.event_log.build_filter('10/30/2017', None, None, None, None, '+0500')

        self.assertEqual(expected, result)

    def test_build_filter_max_date_pos_utc(self):
        expected = {
            'eventCreateDate': {
                'operation': 'lessThanDate',
                'options': [
                    {
                        'name': 'date',
                        'value': [
                            '2017-10-31T00:00:00.000000+05:00'
                        ]
                    }
                ]
            }
        }

        result = self.event_log.build_filter(None, '10/31/2017', None, None, None, '+0500')

        self.assertEqual(expected, result)

    def test_build_filter_min_max_date_pos_utc(self):
        expected = {
            'eventCreateDate': {
                'operation': 'betweenDate',
                'options': [
                    {
                        'name': 'startDate',
                        'value': [
                            '2017-10-30T00:00:00.000000+05:00'
                        ]
                    },
                    {
                        'name': 'endDate',
                        'value': [
                            '2017-10-31T00:00:00.000000+05:00'
                        ]
                    }
                ]
            }
        }

        result = self.event_log.build_filter('10/30/2017', '10/31/2017', None, None, None, '+0500')

        self.assertEqual(expected, result)

    def test_build_filter_min_date_neg_utc(self):
        expected = {
            'eventCreateDate': {
                'operation': 'greaterThanDate',
                'options': [
                    {
                        'name': 'date',
                        'value': [
                            '2017-10-30T00:00:00.000000-03:00'
                        ]
                    }
                ]
            }
        }

        result = self.event_log.build_filter('10/30/2017', None, None, None, None, '-0300')

        self.assertEqual(expected, result)

    def test_build_filter_max_date_neg_utc(self):
        expected = {
            'eventCreateDate': {
                'operation': 'lessThanDate',
                'options': [
                    {
                        'name': 'date',
                        'value': [
                            '2017-10-31T00:00:00.000000-03:00'
                        ]
                    }
                ]
            }
        }

        result = self.event_log.build_filter(None, '10/31/2017', None, None, None, '-0300')

        self.assertEqual(expected, result)

    def test_build_filter_min_max_date_neg_utc(self):
        expected = {
            'eventCreateDate': {
                'operation': 'betweenDate',
                'options': [
                    {
                        'name': 'startDate',
                        'value': [
                            '2017-10-30T00:00:00.000000-03:00'
                        ]
                    },
                    {
                        'name': 'endDate',
                        'value': [
                            '2017-10-31T00:00:00.000000-03:00'
                        ]
                    }
                ]
            }
        }

        result = self.event_log.build_filter('10/30/2017', '10/31/2017', None, None, None, '-0300')

        self.assertEqual(expected, result)

    def test_build_filter_name(self):
        expected = {'eventName': {'operation': 'Add Security Group'}}

        result = self.event_log.build_filter(None, None, 'Add Security Group', None, None, None)

        self.assertEqual(expected, result)

    def test_build_filter_id(self):
        expected = {'objectId': {'operation': 1}}

        result = self.event_log.build_filter(None, None, None, 1, None, None)

        self.assertEqual(expected, result)

    def test_build_filter_type(self):
        expected = {'objectName': {'operation': 'CCI'}}

        result = self.event_log.build_filter(None, None, None, None, 'CCI', None)

        self.assertEqual(expected, result)
