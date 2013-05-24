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
        self.client['Dns_Domain'].getByDomainName.return_value = zone_list
        res = self.dns_client.get_zone('example.com')
        self.assertEqual(res, zone_list[1])

        # no match
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

        self.client['Dns_Domain'].getByDomainName.return_value = [{
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
