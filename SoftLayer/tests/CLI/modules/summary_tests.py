"""
    SoftLayer.tests.CLI.modules.summary_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.tests import TestCase, FixtureClient
from SoftLayer.CLI.modules import summary
from SoftLayer.CLI.environment import Environment
from SoftLayer.CLI.helpers import format_output


class SummaryTests(TestCase):
    def set_up(self):
        self.client = FixtureClient()

    def test_summary(self):
        command = summary.Summary(client=self.client, env=Environment())

        output = command.execute({})
        expected = [{'datacenter': 'dal00',
                     'networking': 1,
                     'subnets': 0,
                     'hardware': 1,
                     'IPs': 3,
                     'vs': 1,
                     'vlans': 1}]
        self.assertEqual(expected, format_output(output, 'python'))
