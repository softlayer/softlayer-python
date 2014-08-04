"""
    SoftLayer.tests.CLI.modules.globalip_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI.modules import globalip
from SoftLayer import testing


class DnsTests(testing.TestCase):
    def set_up(self):
        self.client = testing.FixtureClient()

    def test_ip_assign(self):
        command = globalip.GlobalIpAssign(client=self.client)

        output = command.execute({'<identifier>': '1',
                                  '<target>': '127.0.0.1'})
        self.assertEqual(None, output)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_ip_cancel(self, no_going_back_mock):
        no_going_back_mock.return_value = True
        command = globalip.GlobalIpCancel(client=self.client)

        output = command.execute({'<identifier>': '1', '--really': False})
        self.assertEqual(None, output)

        no_going_back_mock.return_value = False

        self.assertRaises(exceptions.CLIAbort,
                          command.execute,
                          {'<identifier>': '1', '--really': False})

    def test_ip_list(self):
        command = globalip.GlobalIpList(client=self.client)

        output = command.execute({'--v4': True})
        self.assertEqual([{'assigned': 'Yes',
                           'id': '200',
                           'ip': '127.0.0.1',
                           'target': '127.0.0.1 (example.com)'},
                          {'assigned': 'Yes',
                           'id': '201',
                           'ip': '127.0.0.1',
                           'target': '127.0.0.1 (example.com)'}],
                         formatting.format_output(output, 'python'))

        output = command.execute({'--v6': True})
        self.assertEqual([{'assigned': 'Yes',
                           'id': '200',
                           'ip': '127.0.0.1',
                           'target': '127.0.0.1 (example.com)'},
                          {'assigned': 'Yes',
                           'id': '201',
                           'ip': '127.0.0.1',
                           'target': '127.0.0.1 (example.com)'}],
                         formatting.format_output(output, 'python'))
