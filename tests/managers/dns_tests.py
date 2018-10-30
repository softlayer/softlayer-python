"""
    SoftLayer.tests.managers.dns_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer
from SoftLayer import fixtures
from SoftLayer import testing


class DNSTests(testing.TestCase):

    def set_up(self):
        self.dns_client = SoftLayer.DNSManager(self.client)

    def test_list_zones(self):
        zones = self.dns_client.list_zones()

        self.assertEqual(zones, fixtures.SoftLayer_Account.getDomains)

    def test_get_zone(self):
        # match, with defaults
        res = self.dns_client.get_zone(12345)

        self.assertEqual(res, fixtures.SoftLayer_Dns_Domain.getObject)
        self.assert_called_with('SoftLayer_Dns_Domain', 'getObject',
                                identifier=12345,
                                mask='mask[resourceRecords]')

    def test_get_zone_without_records(self):
        self.dns_client.get_zone(12345, records=False)

        self.assert_called_with('SoftLayer_Dns_Domain', 'getObject',
                                identifier=12345,
                                mask=None)

    def test_resolve_zone_name(self):
        res = self.dns_client._get_zone_id_from_name('example.com')

        self.assertEqual([12345], res)
        _filter = {"domains": {"name": {"operation": "_= example.com"}}}
        self.assert_called_with('SoftLayer_Account', 'getDomains',
                                filter=_filter)

    def test_resolve_zone_name_no_matches(self):
        mock = self.set_mock('SoftLayer_Account', 'getDomains')
        mock.return_value = []

        res = self.dns_client._get_zone_id_from_name('example.com')

        self.assertEqual([], res)
        _filter = {"domains": {"name": {"operation": "_= example.com"}}}
        self.assert_called_with('SoftLayer_Account', 'getDomains',
                                filter=_filter)

    def test_create_zone(self):
        res = self.dns_client.create_zone('example.com', serial='2014110201')

        args = ({'serial': '2014110201',
                 'name': 'example.com',
                 'resourceRecords': {}},)
        self.assert_called_with('SoftLayer_Dns_Domain', 'createObject',
                                args=args)
        self.assertEqual(res, {'name': 'example.com'})

    def test_delete_zone(self):
        self.dns_client.delete_zone(1)
        self.assert_called_with('SoftLayer_Dns_Domain', 'deleteObject',
                                identifier=1)

    def test_edit_zone(self):
        self.dns_client.edit_zone('example.com')

        self.assert_called_with('SoftLayer_Dns_Domain', 'editObject',
                                args=('example.com',))

    def test_create_record(self):
        res = self.dns_client.create_record(1, 'test', 'TXT', 'testing',
                                            ttl=1200)

        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'createObject',
                                args=({
                                    'domainId': 1,
                                    'ttl': 1200,
                                    'host': 'test',
                                    'type': 'TXT',
                                    'data': 'testing'
                                },))
        self.assertEqual(res, {'name': 'example.com'})

    def test_create_record_mx(self):
        res = self.dns_client.create_record_mx(1, 'test', 'testing', ttl=1200, priority=21)

        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'createObject',
                                args=({
                                    'domainId': 1,
                                    'ttl': 1200,
                                    'host': 'test',
                                    'type': 'MX',
                                    'data': 'testing',
                                    'mxPriority': 21
                                },))
        self.assertEqual(res, {'name': 'example.com'})

    def test_create_record_srv(self):
        res = self.dns_client.create_record_srv(1, 'record', 'test_data', 'SLS', 8080, 'foobar',
                                                ttl=1200, priority=21, weight=15)

        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'createObject',
                                args=({
                                    'complexType': 'SoftLayer_Dns_Domain_ResourceRecord_SrvType',
                                    'domainId': 1,
                                    'ttl': 1200,
                                    'host': 'record',
                                    'type': 'SRV',
                                    'data': 'test_data',
                                    'priority': 21,
                                    'weight': 15,
                                    'service': 'foobar',
                                    'port': 8080,
                                    'protocol': 'SLS'
                                },))
        self.assertEqual(res, {'name': 'example.com'})

    def test_create_record_ptr(self):
        res = self.dns_client.create_record_ptr('test', 'testing', ttl=1200)

        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'createObject',
                                args=({
                                    'ttl': 1200,
                                    'host': 'test',
                                    'type': 'PTR',
                                    'data': 'testing'
                                },))
        self.assertEqual(res, {'name': 'example.com'})

    def test_generate_create_dict(self):
        data = self.dns_client._generate_create_dict('foo', 'pmx', 'bar', 60, domainId=1234,
                                                     mxPriority=18, port=80, protocol='TCP', weight=25)

        assert_data = {
            'host': 'foo',
            'data': 'bar',
            'ttl': 60,
            'type': 'pmx',
            'domainId': 1234,
            'mxPriority': 18,
            'port': 80,
            'protocol': 'TCP',
            'weight': 25
        }

        self.assertEqual(data, assert_data)

    def test_delete_record(self):
        self.dns_client.delete_record(1)

        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'deleteObject',
                                identifier=1)

    def test_edit_record(self):
        self.dns_client.edit_record({'id': 1, 'name': 'test', 'ttl': '1800'})

        self.assert_called_with('SoftLayer_Dns_Domain_ResourceRecord',
                                'editObject',
                                args=({'id': 1,
                                       'name': 'test',
                                       'ttl': '1800'},),
                                identifier=1)

    def test_dump_zone(self):
        self.dns_client.dump_zone(1)

        self.assert_called_with('SoftLayer_Dns_Domain', 'getZoneFileContents',
                                identifier=1)

    def test_get_record(self):
        # maybe valid domain, but no records matching
        mock = self.set_mock('SoftLayer_Dns_Domain', 'getResourceRecords')
        mock.return_value = []
        self.assertEqual(self.dns_client.get_records(12345), [])

        mock.reset_mock()
        records = fixtures.SoftLayer_Dns_Domain.getResourceRecords
        mock.return_value = [records[0]]
        self.dns_client.get_records(12345,
                                    record_type='a',
                                    host='hostname',
                                    data='a',
                                    ttl='86400')

        _filter = {'resourceRecords': {'type': {'operation': '_= a'},
                                       'host': {'operation': '_= hostname'},
                                       'data': {'operation': '_= a'},
                                       'ttl': {'operation': 86400}}}
        self.assert_called_with('SoftLayer_Dns_Domain', 'getResourceRecords',
                                identifier=12345,
                                filter=_filter)
