"""
    SoftLayer.tests.managers.dns_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import DNSManager
from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.tests.fixtures import Dns_Domain, Account

from mock import ANY


class DNSTests(unittest.TestCase):

    def setUp(self):
        self.client = FixtureClient()
        self.dns_client = DNSManager(self.client)

    def test_init_exercise(self):
        self.assertTrue(hasattr(self.dns_client, 'service'))
        self.assertTrue(hasattr(self.dns_client, 'record'))

    def test_list_zones(self):
        zones = self.dns_client.list_zones()
        self.assertEqual(zones, Account.getDomains)

    def test_get_zone(self):
        # match, with defaults
        res = self.dns_client.get_zone(12345)
        self.assertEqual(res, Dns_Domain.getObject)
        self.client['Dns_Domain'].getObject.assert_called_once_with(
            id=12345,
            mask='resourceRecords')

        # No records masked in
        self.client['Dns_Domain'].getObject.reset_mock()
        self.dns_client.get_zone(12345, records=False)
        self.client['Dns_Domain'].getObject.assert_called_once_with(
            id=12345,
            mask=None)

    def test_resolve_zone_name(self):
        # matching domain
        res = self.dns_client._get_zone_id_from_name('example.com')
        self.assertEqual([12345], res)
        self.client['Account'].getDomains.assert_called_once_with(
            filter={"domains": {"name": {"operation": "_= example.com"}}})

        # no matches
        self.client['Account'].getDomains.reset_mock()
        self.client['Account'].getDomains.return_value = []
        res = self.dns_client._get_zone_id_from_name('example.com')
        self.assertEqual([], res)
        self.client['Account'].getDomains.assert_called_once_with(
            filter={"domains": {"name": {"operation": "_= example.com"}}})

    def test_create_zone(self):
        res = self.dns_client.create_zone('example.com')

        self.client['Dns_Domain'].createObject.assert_called_once_with({
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

    def test_edit_record(self):
        self.dns_client.edit_record({'id': 1, 'name': 'test', 'ttl': '1800'})
        f = self.client['Dns_Domain_ResourceRecord'].editObject
        f.assert_called_once_with(
            {'id': 1, 'name': 'test', 'ttl': '1800'},
            id=1
        )

    def test_dump_zone(self):
        f = self.client['Dns_Domain'].getZoneFileContents
        self.dns_client.dump_zone(1)
        f.assert_called_once_with(id=1)

    def test_get_record(self):
        D = self.client['Dns_Domain'].getResourceRecords

        # maybe valid domain, but no records matching
        D.return_value = []
        self.assertEqual(self.dns_client.get_records(12345), [])

        D.reset_mock()
        D.return_value = [Dns_Domain.getResourceRecords[0]]
        self.dns_client.get_records(12345,
                                    record_type='a',
                                    host='hostname',
                                    data='a',
                                    ttl='86400')
        D.assert_called_once_with(
            id=12345,
            filter={'resourceRecords': {'type': {'operation': '_= a'},
                                        'host': {'operation': '_= hostname'},
                                        'data': {'operation': '_= a'},
                                        'ttl': {'operation': 86400}}},
            mask=ANY)
