"""
    SoftLayer.tests.managers.dns_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from SoftLayer import DNSManager, DNSZoneNotFound

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
from mock import MagicMock, ANY


class DNSTests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.dns_client = DNSManager(self.client)

    def test_init_exercise(self):
        self.assertTrue(hasattr(self.dns_client, 'service'))
        self.assertTrue(hasattr(self.dns_client, 'record'))

    def test_list_zones(self):
        zone_list = ['test']
        self.client['Account'].getDomains.return_value = zone_list
        zones = self.dns_client.list_zones()
        self.assertEqual(zones, zone_list)

    def test_get_zone(self):
        zone_list = [
            {'name': 'test-example.com'},
            {'name': 'example.com'},
        ]

        # match
        self.client['Account'].getDomains.return_value = [zone_list[1]]
        res = self.dns_client.get_zone('example.com')
        self.assertEqual(res, zone_list[1])

        # no match
        self.client['Account'].getDomains.return_value = []
        self.assertRaises(
            DNSZoneNotFound,
            self.dns_client.get_zone,
            'shouldnt-match.com')

    def test_create_zone(self):
        call = self.client['Dns_Domain'].createObject
        call.return_value = {'name': 'example.com'}

        res = self.dns_client.create_zone('example.com')

        call.assert_called_once_with({
            'name': 'example.com', "resourceRecords": {}, "serial": ANY
        })

        self.assertEqual(res, {'name': 'example.com'})

    def test_delete_zone(self):
        self.dns_client.delete_zone(1)
        self.client['Dns_Domain'].deleteObject.assert_called_once_with(id=1)

    def test_edit_zone(self):
        self.dns_client.edit_zone('example.com')
        self.client['Dns_Domain'].editObject.assert_called_once_with(
            'example.com')

    def test_create_record(self):
        self.dns_client.create_record(1, 'test', 'TXT', 'testing', ttl=1200)

        f = self.client['Dns_Domain_ResourceRecord'].createObject
        f.assert_called_once_with(
            {
                'domainId': 1,
                'ttl': 1200,
                'host': 'test',
                'type': 'TXT',
                'data': 'testing'
            })

    def test_delete_record(self):
        self.dns_client.delete_record(1)
        f = self.client['Dns_Domain_ResourceRecord'].deleteObject
        f.assert_called_once_with(id=1)

    def test_search_record(self):

        self.client['Account'].getDomains.return_value = [{
            'name': 'example.com',
            'resourceRecords': [
                {'host': 'TEST1'},
                {'host': 'test2'},
                {'host': 'test3'},
            ]
        }]

        res = self.dns_client.search_record('example.com', 'test1')
        self.assertEqual(res, [{'host': 'TEST1'}])

    def test_edit_record(self):
        self.dns_client.edit_record({'id': 1, 'name': 'test'})
        f = self.client['Dns_Domain_ResourceRecord'].editObject
        f.assert_called_once_with(
            {'id': 1, 'name': 'test'},
            id=1
        )

    def test_dump_zone(self):
        f = self.client['Dns_Domain'].getZoneFileContents
        f.return_value = 'lots of text'
        self.dns_client.dump_zone(1)
        f.assert_called_once_with(id=1)

    def test_get_record(self):
        domain = {'id': 12345, 'name': 'example.com'}
        records = [
            {'ttl': 7200, 'data': 'd', 'host': 'a', 'type': 'cname'},
            {'ttl': 900, 'data': '1', 'host': 'b', 'type': 'a'},
            {'ttl': 900, 'data': 'x', 'host': 'c', 'type': 'ptr'},
            {'ttl': 86400, 'data': 'b', 'host': 'd', 'type': 'txt'},
            {'ttl': 86400, 'data': 'b', 'host': 'e', 'type': 'txt'},
            {'ttl': 600, 'data': 'b', 'host': 'f', 'type': 'txt'},
        ]

        A = self.client['Account'].getDomains
        D = self.client['Dns_Domain'].getResourceRecords

        # Invalid domain
        A.return_value = []
        self.assertRaises(DNSZoneNotFound,
                          self.dns_client.get_records,
                          'example-not.com')

        # valid domain, but no records matching
        A.return_value = [domain]
        D.return_value = []
        self.assertEqual(self.dns_client.get_records('example.com'),
                         [])

        D.reset_mock()
        A.return_value = [domain]
        D.return_value = [records[1]]
        self.dns_client.get_records('example.com', type='a')
        D.assert_called_once_with(
                id=domain['id'],
                filter={'resourceRecords': {'type': {"operation": "_= a"}}},
                mask=ANY)

        D.reset_mock()
        A.return_value = [domain]
        D.return_value = [records[0]]
        self.dns_client.get_records('example.com', host='a')
        D.assert_called_once_with(
                id=domain['id'],
                filter={'resourceRecords': {'host': {"operation": "_= a"}}},
                mask=ANY)

        D.reset_mock()
        A.return_value = [domain]
        D.return_value = records[3:5]
        self.dns_client.get_records('example.com', data='a')
        D.assert_called_once_with(
                id=domain['id'],
                filter={'resourceRecords': {'data': {"operation": "_= a"}}},
                mask=ANY)

        D.reset_mock()
        A.return_value = [domain]
        D.return_value = records[3:5]
        self.dns_client.get_records('example.com', ttl='86400')
        D.assert_called_once_with(
                id=domain['id'],
                filter={'resourceRecords': {'ttl': {"operation": 86400}}},
                mask=ANY)
