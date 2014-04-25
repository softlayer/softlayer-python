"""
    SoftLayer.tests.CLI.modules.dns_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from mock import patch

from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.CLI.helpers import format_output
from SoftLayer.CLI.exceptions import CLIAbort
from SoftLayer.CLI.modules import dns


class DnsTests(unittest.TestCase):
    def setUp(self):
        self.client = FixtureClient()

    def test_dump_zone(self):
        command = dns.DumpZone(client=self.client)

        output = command.execute({'<zone>': '1234'})
        self.assertEqual('lots of text', output)

    def test_create_zone(self):
        command = dns.CreateZone(client=self.client)

        output = command.execute({'<zone>': 'example.com'})
        self.assertEqual(None, output)

    @patch('SoftLayer.CLI.modules.dns.no_going_back')
    def test_delete_zone(self, no_going_back_mock):
        no_going_back_mock.return_value = True
        command = dns.DeleteZone(client=self.client)

        output = command.execute({'<zone>': 'example.com', '--really': False})
        self.assertEqual(None, output)

        no_going_back_mock.return_value = False
        command = dns.DeleteZone(client=self.client)

        self.assertRaises(CLIAbort,
                          command.execute, {'<zone>': 'example.com',
                                            '--really': False})

    def test_list_zones(self):
        command = dns.ListZones(client=self.client)

        output = command.execute({'<zone>': None})
        self.assertEqual([{'serial': 2014030728,
                           'updated': '2014-03-07T13:52:31-06:00',
                           'id': 12345, 'zone': 'example.com'}],
                         format_output(output, 'python'))

    def test_list_all_zones(self):
        command = dns.ListZones(client=self.client)

        output = command.execute({'<zone>': 'example.com'})
        self.assertEqual([{'id': 1,
                           'record': 'hostname',
                           'ttl': 100,
                           'type': 'A',
                           'value': 'd'}],
                         format_output(output, 'python'))

    def test_add_record(self):
        command = dns.AddRecord(client=self.client)

        output = command.execute({'<zone>': 'example.com',
                                  '<record>': 'hostname',
                                  '<type>': 'A',
                                  '<data>': 'd',
                                  '--ttl': 100})
        self.assertEqual(None, output)

    def test_edit_record(self):
        command = dns.EditRecord(client=self.client)

        output = command.execute({'<zone>': 'example.com',
                                  '<record>': 'hostname',
                                  '<type>': 'A',
                                  '--data': 'd',
                                  '--id': 1,
                                  '--ttl': 100})
        self.assertEqual(None, output)

        output = command.execute({'<zone>': 'example.com',
                                  '<record>': 'hostname',
                                  '<type>': 'A',
                                  '--data': 'd',
                                  '--id': None,
                                  '--ttl': 100})
        self.assertEqual(None, output)

    @patch('SoftLayer.CLI.modules.dns.no_going_back')
    def test_delete_record(self, no_going_back_mock):
        no_going_back_mock.return_value = True
        command = dns.RecordRemove(client=self.client)
        output = command.execute({'<zone>': 'example.com',
                                  '<record>': 'hostname',
                                  '--id': '1',
                                  '--really': False})
        self.assertEqual([{'record': '1'}], format_output(output, 'python'))

        output = command.execute({'<zone>': 'example.com',
                                  '<record>': 'hostname',
                                  '--id': None,
                                  '--really': False})
        self.assertEqual([{'record': 1}], format_output(output, 'python'))

        no_going_back_mock.return_value = False
        self.assertRaises(CLIAbort, command.execute, {'<zone>': 'example.com',
                                                      '<record>': 'hostname',
                                                      '--id': 1,
                                                      '--really': False})
