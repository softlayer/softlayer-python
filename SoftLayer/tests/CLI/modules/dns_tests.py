"""
    SoftLayer.tests.CLI.modules.dns_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import os.path

import mock

from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI.modules import dns
from SoftLayer import testing
from SoftLayer.testing import fixtures


class DnsTests(testing.TestCase):
    def set_up(self):
        self.client = testing.FixtureClient()
        self.env = mock.MagicMock()

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

    def test_parse_zone_file(self):
        zone_file = """$ORIGIN realtest.com.
$TTL 86400
@ IN SOA ns1.softlayer.com. support.softlayer.com. (
                       2014052300        ; Serial
                       7200              ; Refresh
                       600               ; Retry
                       1728000           ; Expire
                       43200)            ; Minimum

@                      86400    IN NS    ns1.softlayer.com.
@                      86400    IN NS    ns2.softlayer.com.

                        IN MX 10 test.realtest.com.
testing                86400    IN A     127.0.0.1
testing1               86400    IN A     12.12.0.1
server2      IN   A  1.0.3.4
ftp                             IN  CNAME server2
dev.realtest.com    IN  TXT "This is just a test of the txt record"
    IN  AAAA  2001:db8:10::1
spf  IN TXT "v=spf1 ip4:192.0.2.0/24 ip4:198.51.100.123 a"

"""
        expected = [{'data': 'ns1.softlayer.com.',
                     'record': '@',
                     'record_type': 'NS',
                     'ttl': '86400'},
                    {'data': 'ns2.softlayer.com.',
                     'record': '@',
                     'record_type': 'NS',
                     'ttl': '86400'},
                    {'data': '127.0.0.1',
                     'record': 'testing',
                     'record_type': 'A',
                     'ttl': '86400'},
                    {'data': '12.12.0.1',
                     'record': 'testing1',
                     'record_type': 'A',
                     'ttl': '86400'},
                    {'data': '1.0.3.4',
                     'record': 'server2',
                     'record_type': 'A',
                     'ttl': None},
                    {'data': 'server2',
                     'record': 'ftp',
                     'record_type': 'CNAME',
                     'ttl': None},
                    {'data': '"This is just a test of the txt record"',
                     'record': 'dev.realtest.com',
                     'record_type': 'TXT',
                     'ttl': None},
                    {'data': '"v=spf1 ip4:192.0.2.0/24 ip4:198.51.100.123 a"',
                     'record': 'spf',
                     'record_type': 'TXT',
                     'ttl': None}]
        zone, records, bad_lines = dns.parse_zone_details(zone_file)
        self.assertEqual(zone, 'realtest.com')
        self.assertEqual(records, expected)
        self.assertEqual(len(bad_lines), 13)

    def test_import_zone_dry_run(self):
        command = dns.ImportZone(client=self.client, env=self.env)
        path = os.path.join(testing.FIXTURE_PATH, 'realtest.com')
        output = command.execute({
            '<file>': path,
            '--dry-run': True,
        })

        # Dry run should not result in create calls
        self.assertFalse(self.client['Dns_Domain'].createObject.called)
        record_service = self.client['Dns_Domain_ResourceRecord']
        self.assertFalse(record_service.createObject.called)

        self.assertEqual(None, output)

    def test_import_zone(self):
        command = dns.ImportZone(client=self.client, env=self.env)
        path = os.path.join(testing.FIXTURE_PATH, 'realtest.com')
        output = command.execute({
            '<file>': path,
            '--dry-run': False,
        })

        self.assertFalse(self.client['Dns_Domain'].createObject.called)
        record_service = self.client['Dns_Domain_ResourceRecord']
        self.assertEqual(record_service.createObject.call_args_list,
                         [mock.call({'data': 'ns1.softlayer.com.',
                                     'host': '@',
                                     'domainId': 12345,
                                     'type': 'NS',
                                     'ttl': '86400'}),
                          mock.call({'data': 'ns2.softlayer.com.',
                                     'host': '@',
                                     'domainId': 12345,
                                     'type': 'NS',
                                     'ttl': '86400'}),
                          mock.call({'data': '127.0.0.1',
                                     'host': 'testing',
                                     'domainId': 12345,
                                     'type': 'A',
                                     'ttl': '86400'}),
                          mock.call({'data': '12.12.0.1',
                                     'host': 'testing1',
                                     'domainId': 12345,
                                     'type': 'A',
                                     'ttl': '86400'}),
                          mock.call({'data': '1.0.3.4',
                                     'host': 'server2',
                                     'domainId': 12345,
                                     'type': 'A',
                                     'ttl': None}),
                          mock.call({'data': 'server2',
                                     'host': 'ftp',
                                     'domainId': 12345,
                                     'type': 'CNAME',
                                     'ttl': None}),
                          mock.call({'data':
                                     '"This is just a test of the txt record"',
                                     'host': 'dev.realtest.com',
                                     'domainId': 12345,
                                     'type': 'TXT',
                                     'ttl': None}),
                          mock.call({'data': '"v=spf1 ip4:192.0.2.0/24 '
                                             'ip4:198.51.100.123 a -all"',
                                     'host': 'spf',
                                     'domainId': 12345,
                                     'type': 'TXT',
                                     'ttl': None})])

        self.assertEqual("Finished", output)
