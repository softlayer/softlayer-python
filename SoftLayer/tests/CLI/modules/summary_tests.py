"""
    SoftLayer.tests.CLI.modules.summary_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI.modules import summary
from SoftLayer import testing


class SummaryTests(testing.TestCase):
    def set_up(self):
        self.client = testing.FixtureClient()

    def test_summary(self):
        command = summary.Summary(client=self.client,
                                  env=environment.Environment())

        output = command.execute({})
        expected = [{'datacenter': 'dal00',
                     'networking': 1,
                     'subnets': 0,
                     'hardware': 1,
                     'IPs': 3,
                     'vs': 1,
                     'vlans': 1}]
        self.assertEqual(expected, formatting.format_output(output, 'python'))
