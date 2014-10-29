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
                'networking': 1,
                'subnets': 0,
                'hardware': 1,
                'ips': 6,
                'vs': 1,
                'vlans': 3
            }
        ]

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output), expected)
