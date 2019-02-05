"""
    SoftLayer.tests.CLI.modules.event_log_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :license: MIT, see LICENSE for more details.
"""

import json

from SoftLayer import testing


class EventLogTests(testing.TestCase):
    def test_get_event_log(self):
        expected = [
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

        result = self.run_command(['audit-log', 'get'])

        self.assert_no_fail(result)
        self.assertEqual(expected, json.loads(result.output))

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

        result = self.run_command(['audit-log', 'types'])

        self.assert_no_fail(result)
        self.assertEqual(expected, json.loads(result.output))
