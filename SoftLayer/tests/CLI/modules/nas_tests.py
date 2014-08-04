"""
    SoftLayer.tests.CLI.modules.nas_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.CLI import formatting
from SoftLayer.CLI.modules import nas
from SoftLayer import testing


class RWhoisTests(testing.TestCase):
    def set_up(self):
        self.client = testing.FixtureClient()

    def test_list_nas(self):
        command = nas.ListNAS(client=self.client)
        output = command.execute({})

        self.assertEqual([{'username': 'user',
                           'datacenter': 'Dallas',
                           'server': '127.0.0.1',
                           'password': 'pass',
                           'id': 1,
                           'size': 10}],
                         formatting.format_output(output, 'python'))
