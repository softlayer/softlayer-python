"""
    SoftLayer.tests.CLI.modules.summary_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import testing

import json


class SummaryTests(testing.TestCase):

    def test_summary(self):
        result = self.run_command(['summary'])

        expected = [
            {
                'datacenter': 'dal00',
                'subnets': 0,
                'hardware': 1,
                'public_ips': 6,
                'virtual_servers': 1,
                'vlans': 3
            }
        ]

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), expected)
