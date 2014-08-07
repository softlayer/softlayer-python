"""
    SoftLayer.tests.CLI.modules.dns_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI.modules import dns
from SoftLayer import testing
from SoftLayer.testing import fixtures


class DnsTests(testing.TestCase):
    def set_up(self):
        self.client = testing.FixtureClient()

    def test_dump_zone(self):
        command = dns.DumpZone(client=self.client)

        output = command.execute({'<zone>': '1234'})
        self.assertEqual('lots of text', output)

    def test_create_zone(self):
        command = dns.CreateZone(client=self.client)

        output = command.execute({'<zone>': 'example.com'})
        self.assertEqual(None, output)

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_delete_zone(self, no_going_back_mock):
        no_going_back_mock.return_value = True
        command = dns.DeleteZone(client=self.client)

        output = command.execute({'<zone>': 'example.com', '--really': False})
        self.assertEqual(None, output)

        no_going_back_mock.return_value = False
        command = dns.DeleteZone(client=self.client)

        self.assertRaises(exceptions.CLIAbort,
                          command.execute, {'<zone>': 'example.com',
                                            '--really': False})

    def test_list_zones(self):
        command = dns.ListZones(client=self.client)

        output = command.execute({'<zone>': None})
        self.assertEqual([{'serial': 2014030728,
                           'updated': '2014-03-07T13:52:31-06:00',
                           'id': 12345, 'zone': 'example.com'}],
                         formatting.format_output(output, 'python'))

    def test_list_all_zones(self):
        command = dns.ListZones(client=self.client)

        output = command.execute({'<zone>': 'example.com'})
        self.assertEqual({'record': 'a',
                          'type': 'CNAME',
                          'id': 1,
                          'value': 'd',
                          'ttl': 100},
                         formatting.format_output(output, 'python')[0])

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

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_delete_record(self, no_going_back_mock):
        no_going_back_mock.return_value = True
        self.client['Dns_Domain'].getResourceRecords.return_value = [
            fixtures.Dns_Domain.getResourceRecords[0]]
        command = dns.RecordRemove(client=self.client)
        output = command.execute({'<zone>': 'example.com',
                                  '<record>': 'hostname',
                                  '--id': '1',
                                  '--really': False})
        self.assertEqual([{'record': '1'}],
                         formatting.format_output(output, 'python'))

        output = command.execute({'<zone>': 'example.com',
                                  '<record>': 'hostname',
                                  '--id': None,
                                  '--really': False})
        self.assertEqual([{'record': 1}],
                         formatting.format_output(output, 'python'))

        no_going_back_mock.return_value = False
        self.assertRaises(exceptions.CLIAbort,
                          command.execute, {'<zone>': 'example.com',
                                            '<record>': 'hostname',
                                            '--id': 1,
                                            '--really': False})
