"""
    SoftLayer.tests.CLI.modules.event_log_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :license: MIT, see LICENSE for more details.
"""

import json

from SoftLayer.CLI import formatting
from SoftLayer import testing


class EventLogTests(testing.TestCase):
    def test_get_event_log_with_metadata(self):
        expected = [
            {
                'date': '2017-10-23T14:22:36.221541-05:00',
                'event': 'Disable Port',
                'object': 'test.softlayer.com',
                'username': 'SYSTEM',
                'type': 'CCI',
                'metadata': ''
            },
            {
                'date': '2017-10-18T09:40:41.830338-05:00',
                'event': 'Security Group Rule Added',
                'object': 'test.softlayer.com',
                'username': 'SL12345-test',
                'type': 'CCI',
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
                'object': 'test.softlayer.com',
                'username': 'SL12345-test',
                'type': 'CCI',
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
                'object': 'test_SG',
                'username': 'SL12345-test',
                'type': 'Security Group',
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
                'object': 'test_SG',
                'username': 'SL12345-test',
                'type': 'Security Group',
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
                'object': 'test_SG',
                'username': 'SL12345-test',
                'type': 'Security Group',
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
                'object': 'test_SG',
                'username': 'SL12345-test',
                'type': 'Security Group',
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

        result = self.run_command(['event-log', 'get', '--metadata'])

        self.assert_no_fail(result)
        self.assertEqual(expected, json.loads(result.output))

    def test_get_event_log_without_metadata(self):
        expected = [
            {
                'date': '2017-10-23T14:22:36.221541-05:00',
                'event': 'Disable Port',
                'username': 'SYSTEM',
                'type': 'CCI',
                'object': 'test.softlayer.com'
            },
            {
                'date': '2017-10-18T09:40:41.830338-05:00',
                'event': 'Security Group Rule Added',
                'username': 'SL12345-test',
                'type': 'CCI',
                'object': 'test.softlayer.com'
            },
            {
                'date': '2017-10-18T09:40:32.238869-05:00',
                'event': 'Security Group Added',
                'username': 'SL12345-test',
                'type': 'CCI',
                'object': 'test.softlayer.com'
            },
            {
                'date': '2017-10-18T10:42:13.089536-05:00',
                'event': 'Security Group Rule(s) Removed',
                'username': 'SL12345-test',
                'type': 'Security Group',
                'object': 'test_SG'
            },
            {
                'date': '2017-10-18T10:42:11.679736-05:00',
                'event': 'Network Component Removed from Security Group',
                'username': 'SL12345-test',
                'type': 'Security Group',
                'object': 'test_SG'
            },
            {
                'date': '2017-10-18T10:41:49.802498-05:00',
                'event': 'Security Group Rule(s) Added',
                'username': 'SL12345-test',
                'type': 'Security Group',
                'object': 'test_SG'
            },
            {
                'date': '2017-10-18T10:41:42.176328-05:00',
                'event': 'Network Component Added to Security Group',
                'username': 'SL12345-test',
                'type': 'Security Group',
                'object': 'test_SG'
            }
        ]

        result = self.run_command(['event-log', 'get'])

        self.assert_no_fail(result)
        self.assertEqual(expected, json.loads(result.output))

    def test_get_event_table(self):
        table_fix = formatting.Table(['event', 'object', 'type', 'date', 'username', 'metadata'])
        table_fix.align['metadata'] = "l"
        expected = [
            {
                'date': '2017-10-23T14:22:36.221541-05:00',
                'event': 'Disable Port',
                'object': 'test.softlayer.com',
                'username': 'SYSTEM',
                'type': 'CCI',
                'metadata': ''
            },
            {
                'date': '2017-10-18T09:40:41.830338-05:00',
                'event': 'Security Group Rule Added',
                'object': 'test.softlayer.com',
                'username': 'SL12345-test',
                'type': 'CCI',
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
                'object': 'test.softlayer.com',
                'username': 'SL12345-test',
                'type': 'CCI',
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
                'object': 'test_SG',
                'username': 'SL12345-test',
                'type': 'Security Group',
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
                'object': 'test_SG',
                'username': 'SL12345-test',
                'type': 'Security Group',
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
                'object': 'test_SG',
                'username': 'SL12345-test',
                'type': 'Security Group',
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
                'object': 'test_SG',
                'username': 'SL12345-test',
                'type': 'Security Group',
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

        for log in expected:
            table_fix.add_row([log['event'], log['object'], log['type'], log['date'],
                              log['username'], log['metadata'].strip("{}\n\t")])
        expected_output = formatting.format_output(table_fix) + '\n'

        result = self.run_command(args=['event-log', 'get', '--metadata'], fmt='table')

        self.assert_no_fail(result)
        self.assertEqual(expected_output, result.output)

    def test_get_event_log_empty(self):
        mock = self.set_mock('SoftLayer_Event_Log', 'getAllObjects')
        mock.return_value = None

        result = self.run_command(['event-log', 'get'])

        self.assertEqual(mock.call_count, 1)
        self.assert_no_fail(result)
        self.assertEqual('"None available."\n', result.output)

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
