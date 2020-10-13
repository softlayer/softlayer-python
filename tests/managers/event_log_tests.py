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
        # Cast to list to force generator to get all objects
        result = list(self.event_log.get_event_logs())

        expected = fixtures.SoftLayer_Event_Log.getAllObjects
        self.assertEqual(expected, result)
        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects')

    def test_get_event_logs_no_iteration(self):
        # Cast to list to force generator to get all objects
        result = self.event_log.get_event_logs(iterator=False)

        expected = fixtures.SoftLayer_Event_Log.getAllObjects
        self.assertEqual(expected, result)
        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects')

    def test_get_event_log_types(self):
        result = self.event_log.get_event_log_types()

        expected = fixtures.SoftLayer_Event_Log.getAllEventObjectNames
        self.assertEqual(expected, result)
        self.assert_called_with('SoftLayer_Event_Log', 'getAllEventObjectNames')

    def test_build_filter_no_args(self):
        result = self.event_log.build_filter(None, None, None, None, None, None)

        self.assertEqual(result, {})

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
