"""
    SoftLayer.tests.CLI.modules.globalip_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from mock import patch

from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.CLI.helpers import format_output
from SoftLayer.CLI.exceptions import CLIAbort
from SoftLayer.CLI.modules import globalip


class DnsTests(unittest.TestCase):
    def setUp(self):
        self.client = FixtureClient()

    def test_ip_assign(self):
        command = globalip.GlobalIpAssign(client=self.client)

        output = command.execute({'<identifier>': '1',
                                  '<target>': '127.0.0.1'})
        self.assertEqual(None, output)

    @patch('SoftLayer.CLI.modules.globalip.no_going_back')
    def test_ip_cancel(self, no_going_back_mock):
        no_going_back_mock.return_value = True
        command = globalip.GlobalIpCancel(client=self.client)

        output = command.execute({'<identifier>': '1', '--really': False})
        self.assertEqual(None, output)

        no_going_back_mock.return_value = False

        self.assertRaises(CLIAbort,
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
                         format_output(output, 'python'))

        output = command.execute({'--v6': True})
        self.assertEqual([{'assigned': 'Yes',
                           'id': '200',
                           'ip': '127.0.0.1',
                           'target': '127.0.0.1 (example.com)'},
                          {'assigned': 'Yes',
                           'id': '201',
                           'ip': '127.0.0.1',
                           'target': '127.0.0.1 (example.com)'}],
                         format_output(output, 'python'))
