"""
    SoftLayer.tests.CLI.modules.dns_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import json
import os.path

import mock

from SoftLayer.CLI.dns import zone_import
from SoftLayer.CLI import exceptions
from SoftLayer import testing


class DnsTests(testing.TestCase):

    def test_zone_print(self):
        result = self.run_command(['dns', 'zone-print', '1234'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output), "lots of text")

    def test_create_zone(self):
        result = self.run_command(['dns', 'zone-create', 'example.com'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_delete_zone(self, no_going_back_mock):
        no_going_back_mock.return_value = True
        result = self.run_command(['dns', 'zone-delete', '1234'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

        no_going_back_mock.return_value = False
        result = self.run_command(['--really', 'dns', 'zone-delete', '1234'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_delete_zone_abort(self, no_going_back_mock):
        no_going_back_mock.return_value = False
        result = self.run_command(['dns', 'zone-delete', '1234'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

    def test_list_zones(self):
        result = self.run_command(['dns', 'zone-list'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output),
                         [{'serial': 2014030728,
                           'updated': '2014-03-07T13:52:31-06:00',
                           'id': 12345,
                           'zone': 'example.com'}])

    def test_list_records(self):
        result = self.run_command(['dns', 'record-list', '1234'])

        self.assert_no_fail(result)
        self.assertEqual(json.loads(result.output)[0],
                         {'record': 'a',
                          'type': 'CNAME',
                          'id': 1,
                          'data': 'd',
                          'ttl': 7200})

    def test_add_record(self):
        result = self.run_command(['dns', 'record-add', '1234', 'hostname',
                                   'A', 'd', '--ttl=100'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_delete_record(self, no_going_back_mock):
        no_going_back_mock.return_value = True
        result = self.run_command(['dns', 'record-remove', '1234'])

        self.assert_no_fail(result)
        self.assertEqual(result.output, "")

    @mock.patch('SoftLayer.CLI.formatting.no_going_back')
    def test_delete_record_abort(self, no_going_back_mock):
        no_going_back_mock.return_value = False
        result = self.run_command(['dns', 'record-remove', '1234'])

        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, exceptions.CLIAbort)

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
                     'type': 'NS',
                     'ttl': '86400'},
                    {'data': 'ns2.softlayer.com.',
                     'record': '@',
                     'type': 'NS',
                     'ttl': '86400'},
                    {'data': '127.0.0.1',
                     'record': 'testing',
                     'type': 'A',
                     'ttl': '86400'},
                    {'data': '12.12.0.1',
                     'record': 'testing1',
                     'type': 'A',
                     'ttl': '86400'},
                    {'data': '1.0.3.4',
                     'record': 'server2',
                     'type': 'A',
                     'ttl': None},
                    {'data': 'server2',
                     'record': 'ftp',
                     'type': 'CNAME',
                     'ttl': None},
                    {'data': '"This is just a test of the txt record"',
                     'record': 'dev.realtest.com',
                     'type': 'TXT',
                     'ttl': None},
                    {'data': '"v=spf1 ip4:192.0.2.0/24 ip4:198.51.100.123 a"',
                     'record': 'spf',
                     'type': 'TXT',
                     'ttl': None}]
        zone, records, bad_lines = zone_import.parse_zone_details(zone_file)
        self.assertEqual(zone, 'realtest.com')
        self.assertEqual(records, expected)
        self.assertEqual(len(bad_lines), 13)

    def test_import_zone_dry_run(self):
        path = os.path.join(testing.FIXTURE_PATH, 'realtest.com')
        result = self.run_command(['dns', 'import', path, '--dry-run'])

        self.assertIn("Parsed: zone=realtest.com", result.output)
        self.assertIn(
            "Parsed: type=NS, record=@, data=ns1.softlayer.com., ttl=86400",
            result.output)
        self.assertIn("Unparsed: $TTL 86400", result.output)

    def test_import_zone(self):
        path = os.path.join(testing.FIXTURE_PATH, 'realtest.com')
        result = self.run_command(['dns', 'import', path])

        self.assertEqual(self.calls('SoftLayer_Dns_Domain', 'createObject'),
                         [])

        calls = self.calls('SoftLayer_Dns_Domain_ResourceRecord',
                           'createObject')
        expected_calls = [{'data': 'ns1.softlayer.com.',
                           'host': '@',
                           'domainId': 12345,
                           'type': 'NS',
                           'ttl': '86400'},
                          {'data': 'ns2.softlayer.com.',
                           'host': '@',
                           'domainId': 12345,
                           'type': 'NS',
                           'ttl': '86400'},
                          {'data': '127.0.0.1',
                           'host': 'testing',
                           'domainId': 12345,
                           'type': 'A',
                           'ttl': '86400'},
                          {'data': '12.12.0.1',
                           'host': 'testing1',
                           'domainId': 12345,
                           'type': 'A',
                           'ttl': '86400'},
                          {'data': '1.0.3.4',
                           'host': 'server2',
                           'domainId': 12345,
                           'type': 'A',
                           'ttl': None},
                          {'data': 'server2',
                           'host': 'ftp',
                           'domainId': 12345,
                           'type': 'CNAME',
                           'ttl': None},
                          {'data':
                           '"This is just a test of the txt record"',
                           'host': 'dev.realtest.com',
                           'domainId': 12345,
                           'type': 'TXT',
                           'ttl': None},
                          {'data': '"v=spf1 ip4:192.0.2.0/24 '
                                   'ip4:198.51.100.123 a -all"',
                           'host': 'spf',
                           'domainId': 12345,
                           'type': 'TXT',
                           'ttl': None}]

        self.assertEqual(len(calls), len(expected_calls))
        for call, expected_call in zip(calls, expected_calls):
            self.assertEqual(call.args[0], expected_call)

        self.assertIn("Finished", result.output)
