"""
    SoftLayer.tests.CLI.modules.event_log_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :license: MIT, see LICENSE for more details.
"""

import json

from SoftLayer.CLI.event_log import get as event_log_get
from SoftLayer import testing


class EventLogTests(testing.TestCase):

    def test_get_event_log(self):
        result = self.run_command(['audit-log', 'get'])

        self.assert_no_fail(result)

        expected_esponse = [
            {
                'date': '2017-10-23T14:22:36.221541-05:00',
                'event': 'Disable Port',
                'label': 'test.softlayer.com',
                'metadata': ''
            },
            {
                'date': '2017-10-18T09:40:41.830338-05:00',
                'event': 'Security Group Rule Added',
                'label': 'test.softlayer.com',
                'metadata': json.dumps(json.loads(
                        '{"networkComponentId":"100",'
                        '"networkInterfaceType":"public",'
                        '"requestId":"53d0b91d392864e062f4958",'
                        '"rules":[{"direction":"ingress",'
                        '"ethertype":"IPv4",'
                        '"portRangeMax":2001,"portRangeMin":2000,"protocol":"tcp",'
                        '"remoteGroupId":null,"remoteIp":null,"ruleId":"100"}],"securityGroupId":"200",'
                        '"securityGroupName":"test_SG"}'
                    ),
                    indent=4,
                    sort_keys=True
                )
            },
            {
                'date': '2017-10-18T09:40:32.238869-05:00',
                'event': 'Security Group Added',
                'label': 'test.softlayer.com',
                'metadata': json.dumps(json.loads(
                        '{"networkComponentId":"100",'
                        '"networkInterfaceType":"public",'
                        '"requestId":"96c9b47b9e102d2e1d81fba",'
                        '"securityGroupId":"200",'
                        '"securityGroupName":"test_SG"}'
                    ),
                    indent=4,
                    sort_keys=True
                )
            },
            {
                'date': '2017-10-18T10:42:13.089536-05:00',
                'event': 'Security Group Rule(s) Removed',
                'label': 'test_SG',
                'metadata': json.dumps(json.loads(
                        '{"requestId":"2abda7ca97e5a1444cae0b9",'
                        '"rules":[{"direction":"ingress",'
                        '"ethertype":"IPv4",'
                        '"portRangeMax":2001,"portRangeMin":2000,"protocol":"tcp",'
                        '"remoteGroupId":null,"remoteIp":null,"ruleId":"800"}]}'
                    ),
                    indent=4,
                    sort_keys=True
                )
            },
            {
                'date': '2017-10-18T10:42:11.679736-05:00',
                'event': 'Network Component Removed from Security Group',
                'label': 'test_SG',
                'metadata': json.dumps(json.loads(
                        '{"fullyQualifiedDomainName":"test.softlayer.com",'
                        '"networkComponentId":"100",'
                        '"networkInterfaceType":"public",'
                        '"requestId":"6b9a87a9ab8ac9a22e87a00"}'
                    ),
                    indent=4,
                    sort_keys=True
                )
            },
            {
                'date': '2017-10-18T10:41:49.802498-05:00',
                'event': 'Security Group Rule(s) Added',
                'label': 'test_SG',
                'metadata': json.dumps(json.loads(
                        '{"requestId":"0a293c1c3e59e4471da6495",'
                        '"rules":[{"direction":"ingress",'
                        '"ethertype":"IPv4",'
                        '"portRangeMax":2001,"portRangeMin":2000,"protocol":"tcp",'
                        '"remoteGroupId":null,"remoteIp":null,"ruleId":"800"}]}'
                    ),
                    indent=4,
                    sort_keys=True
                )
            },
            {
                'date': '2017-10-18T10:41:42.176328-05:00',
                'event': 'Network Component Added to Security Group',
                'label': 'test_SG',
                'metadata': json.dumps(json.loads(
                        '{"fullyQualifiedDomainName":"test.softlayer.com",'
                        '"networkComponentId":"100",'
                        '"networkInterfaceType":"public",'
                        '"requestId":"4709e02ad42c83f80345904"}'
                    ),
                    indent=4,
                    sort_keys=True
                )
            }
        ]

        self.assertEqual(expected_esponse, json.loads(result.output))

    def test_get_event_log_request_id(self):
        result = self.run_command(['audit-log', 'get', '--request_id=4709e02ad42c83f80345904'])

        # Because filtering doesn't work on the test data recieved from the server we stand up,
        # and we call getAllObjects twice, the dataset we work over has duplicates
        expected_esponse = [
            {
                'date': '2017-10-18T10:41:42.176328-05:00',
                'event': 'Network Component Added to Security Group',
                'label': 'test_SG',
                'metadata': json.dumps(json.loads(
                        '{"fullyQualifiedDomainName":"test.softlayer.com",'
                        '"networkComponentId":"100",'
                        '"networkInterfaceType":"public",'
                        '"requestId":"4709e02ad42c83f80345904"}'
                    ),
                    indent=4,
                    sort_keys=True
                )
            },
            {
                'date': '2017-10-18T10:41:42.176328-05:00',
                'event': 'Network Component Added to Security Group',
                'label': 'test_SG',
                'metadata': json.dumps(json.loads(
                        '{"fullyQualifiedDomainName":"test.softlayer.com",'
                        '"networkComponentId":"100",'
                        '"networkInterfaceType":"public",'
                        '"requestId":"4709e02ad42c83f80345904"}'
                    ),
                    indent=4,
                    sort_keys=True
                )
            }
        ]

        self.assertEqual(expected_esponse, json.loads(result.output))

    def test_get_event_log_date_min(self):
        observed_filter = event_log_get._build_filter('10/30/2017', None, None, None, None, None)

        expected_filter = {
            'eventCreateDate': {
                'operation': 'greaterThanDate',
                'options': [{
                    'name': 'date',
                    'value': ['2017-10-30T00:00:00.000000-05:00']
                }]
            }
        }

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_date_max(self):
        observed_filter = event_log_get._build_filter(None, '10/31/2017', None, None, None, None)

        expected_filter = {
            'eventCreateDate': {
                'operation': 'lessThanDate',
                'options': [{
                    'name': 'date',
                    'value': ['2017-10-31T00:00:00.000000-05:00']
                }]
            }
        }

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_date_min_max(self):
        observed_filter = event_log_get._build_filter('10/30/2017', '10/31/2017', None, None, None, None)

        expected_filter = {
            'eventCreateDate': {
                'operation': 'betweenDate',
                'options': [
                    {
                        'name': 'startDate',
                        'value': ['2017-10-30T00:00:00.000000-05:00']
                    },
                    {
                        'name': 'endDate',
                        'value': ['2017-10-31T00:00:00.000000-05:00']
                    }
                ]
            }
        }

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_date_min_utc_offset(self):
        observed_filter = event_log_get._build_filter('10/30/2017', None, None, None, None, "-0600")

        expected_filter = {
            'eventCreateDate': {
                'operation': 'greaterThanDate',
                'options': [{
                    'name': 'date',
                    'value': ['2017-10-30T00:00:00.000000-06:00']
                }]
            }
        }

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_date_max_utc_offset(self):
        observed_filter = event_log_get._build_filter(None, '10/31/2017', None, None, None, "-0600")

        expected_filter = {
            'eventCreateDate': {
                'operation': 'lessThanDate',
                'options': [{
                    'name': 'date',
                    'value': ['2017-10-31T00:00:00.000000-06:00']
                }]
            }
        }

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_date_min_max_utc_offset(self):
        observed_filter = event_log_get._build_filter('10/30/2017', '10/31/2017', None, None, None, "-0600")

        expected_filter = {
            'eventCreateDate': {
                'operation': 'betweenDate',
                'options': [
                    {
                        'name': 'startDate',
                        'value': ['2017-10-30T00:00:00.000000-06:00']
                    },
                    {
                        'name': 'endDate',
                        'value': ['2017-10-31T00:00:00.000000-06:00']
                    }
                ]
            }
        }

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_event(self):
        observed_filter = event_log_get._build_filter(None, None, 'Security Group Rule Added', None, None, None)

        expected_filter = {'eventName': {'operation': 'Security Group Rule Added'}}

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_id(self):
        observed_filter = event_log_get._build_filter(None, None, None, 1, None, None)

        expected_filter = {'objectId': {'operation': 1}}

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_type(self):
        observed_filter = event_log_get._build_filter(None, None, None, None, 'CCI', None)

        expected_filter = {'objectName': {'operation': 'CCI'}}

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_event_all_args(self):
        observed_filter = event_log_get._build_filter(None, None, 'Security Group Rule Added', 1, 'CCI', None)

        expected_filter = {
            'eventName': {
                'operation': 'Security Group Rule Added'
            },
            'objectId': {
                'operation': 1
            },
            'objectName': {
                'operation': 'CCI'
            }
        }

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_event_all_args_min_date(self):
        observed_filter = event_log_get._build_filter('10/30/2017', None, 'Security Group Rule Added', 1, 'CCI', None)

        expected_filter = {
            'eventCreateDate': {
                'operation': 'greaterThanDate',
                'options': [{
                    'name': 'date',
                    'value': ['2017-10-30T00:00:00.000000-05:00']
                }]
            },
            'eventName': {
                'operation': 'Security Group Rule Added'
            },
            'objectId': {
                'operation': 1
            },
            'objectName': {
                'operation': 'CCI'
            }
        }

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_event_all_args_max_date(self):
        observed_filter = event_log_get._build_filter(None, '10/31/2017', 'Security Group Rule Added', 1, 'CCI', None)

        expected_filter = {
            'eventCreateDate': {
                'operation': 'lessThanDate',
                'options': [{
                    'name': 'date',
                    'value': ['2017-10-31T00:00:00.000000-05:00']
                }]
            },
            'eventName': {
                'operation': 'Security Group Rule Added'
            },
            'objectId': {
                'operation': 1
            },
            'objectName': {
                'operation': 'CCI'
            }
        }

        self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_event_all_args_min_max_date(self):
        observed_filter = event_log_get._build_filter(
            '10/30/2017',
            '10/31/2017',
            'Security Group Rule Added',
            1,
            'CCI',
            None
        )

        expected_filter = {
            'eventCreateDate': {
                'operation': 'betweenDate',
                'options': [
                    {
                        'name': 'startDate',
                        'value': ['2017-10-30T00:00:00.000000-05:00']
                    },
                    {
                        'name': 'endDate',
                        'value': ['2017-10-31T00:00:00.000000-05:00']
                    }
                ]
            },
            'eventName': {
                'operation': 'Security Group Rule Added'
            },
            'objectId': {
                'operation': 1
            },
            'objectName': {
                'operation': 'CCI'
            }
        }

        self.assertEqual(expected_filter, observed_filter)

        def test_get_event_log_event_all_args_min_date_utc_offset(self):
            observed_filter = event_log_get._build_filter(
                '10/30/2017',
                None,
                'Security Group Rule Added',
                1,
                'CCI',
                '-0600'
            )

            expected_filter = {
                'eventCreateDate': {
                    'operation': 'greaterThanDate',
                    'options': [{
                        'name': 'date',
                        'value': ['2017-10-30T00:00:00.000000-06:00']
                    }]
                },
                'eventName': {
                    'operation': 'Security Group Rule Added'
                },
                'objectId': {
                    'operation': 1
                },
                'objectName': {
                    'operation': 'CCI'
                }
            }

            self.assertEqual(expected_filter, observed_filter)

    def test_get_event_log_event_all_args_max_date_utc_offset(self):
        observed_filter = event_log_get._build_filter(
            None,
            '10/31/2017',
            'Security Group Rule Added',
            1,
            'CCI',
            '-0600'
        )

        correct_filter = {
            'eventCreateDate': {
                'operation': 'lessThanDate',
                'options': [{
                    'name': 'date',
                    'value': ['2017-10-31T00:00:00.000000-06:00']
                }]
            },
            'eventName': {
                'operation': 'Security Group Rule Added'
            },
            'objectId': {
                'operation': 1
            },
            'objectName': {
                'operation': 'CCI'
            }
        }

        self.assertEqual(correct_filter, observed_filter)

    def test_get_event_log_event_all_args_min_max_date_utc_offset(self):
        observed_filter = event_log_get._build_filter(
            '10/30/2017',
            '10/31/2017',
            'Security Group Rule Added',
            1,
            'CCI',
            '-0600')

        correct_filter = {
            'eventCreateDate': {
                'operation': 'betweenDate',
                'options': [
                    {
                        'name': 'startDate',
                        'value': ['2017-10-30T00:00:00.000000-06:00']
                    },
                    {
                        'name': 'endDate',
                        'value': ['2017-10-31T00:00:00.000000-06:00']
                    }
                ]
            },
            'eventName': {
                'operation': 'Security Group Rule Added'
            },
            'objectId': {
                'operation': 1
            },
            'objectName': {
                'operation': 'CCI'
            }
        }

        self.assertEqual(correct_filter, observed_filter)

    def test_get_event_log_types(self):
        result = self.run_command(['audit-log', 'types'])

        self.assert_no_fail(result)

        expected_esponse = [
            {
                'types': 'CCI'
            },
            {
                'types': 'Security Group'
            }
        ]

        self.assertEqual(expected_esponse, json.loads(result.output))
