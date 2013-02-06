import SoftLayer
import SoftLayer.CCI

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from mock import MagicMock, ANY, call, patch


class CCITests_unittests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.cci = SoftLayer.CCIManager(self.client)

    def test_list_instances(self):

        all_guests = [call(mask=ANY), call(mask=ANY)]
        other_guests = [call(mask=ANY)]

        self.cci.list_instances(hourly=True, monthly=True)
        self.cci.list_instances(hourly=False, monthly=False)
        self.client.__getitem__().getVirtualGuests.assert_has_calls(all_guests)

        self.cci.list_instances(hourly=False, monthly=True)
        self.client.__getitem__().getMonthlyVirtualGuests.assert_has_calls(other_guests)

        self.cci.list_instances(hourly=True, monthly=False)
        self.client.__getitem__().getHourlyVirtualGuests.assert_has_calls(other_guests)

    def test_get_instance(self):
        self.client.__getitem__().getObject.return_value = {
            'hourlyVirtualGuests': "this is unique"}
        self.cci.get_instance(1)
        self.client.__getitem__().getObject.assert_called_once_with(
            id=1, mask=ANY)

    def test_get_create_options(self):
        self.cci.get_create_options()
        self.client.__getitem__().getCreateObjectOptions.assert_called_once_with()

    def test_cancel_instance(self):
        self.cci.cancel_instance(id=1)
        self.client.__getitem__().deleteObject.assert_called_once_with(id=1)

    @patch('SoftLayer.CCI.CCIManager._generate_create_dict')
    def test_create_verify(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        self.cci.verify_create_instance(test=1, verify=1)
        create_dict.assert_called_once_with(test=1, verify=1)
        self.client.__getitem__().generateOrderTemplate.assert_called_once_with(
            {'test': 1, 'verify': 1})

    @patch('SoftLayer.CCI.CCIManager._generate_create_dict')
    def test_create_instance(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        self.cci.create_instance(test=1, verify=1)
        create_dict.assert_called_once_with(test=1, verify=1)
        self.client.__getitem__().createObject.assert_called_once_with(
            {'test': 1, 'verify': 1})

    def test_generate_os_and_image(self):
        self.assertRaises(
            SoftLayer.CCI.CCICreateMutuallyExclusive,
            self.cci._generate_create_dict,
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code=1,
            image_id=1,
        )

    def test_generate_missing(self):
        self.assertRaises(
            SoftLayer.CCI.CCICreateMissingRequired,
            self.cci._generate_create_dict,
        )

    def test_generate_basic(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
        }

        self.assertEqual(data, assert_data)

    def test_generate_monthly(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            hourly=False,
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
        }

        self.assertEqual(data, assert_data)

    def test_generate_image_id(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            image_id="45",
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'blockDeviceTemplateGroup': {"globalIdentifier": "45"},
            'hourlyBillingFlag': True,
        }

        self.assertEqual(data, assert_data)

    def test_generate_private(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            private=True,
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'dedicatedAccountHostOnlyFlag': True,
        }

        self.assertEqual(data, assert_data)

    def test_generate_datacenter(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            datacenter="sng01",
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'datacenter': {"name": 'sng01'},
        }

        self.assertEqual(data, assert_data)

    def test_generate_public_vlan(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            public_vlan=1,
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'primaryNetworkCompnent': {"networkVlan": {"id": 1}},
        }

        self.assertEqual(data, assert_data)

    def test_generate_private_vlan(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            private_vlan=1,
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'primaryBackendNetworkCompnent': {"networkVlan": {"id": 1}},
        }

        self.assertEqual(data, assert_data)



#    def test_init_exercise(self):
#        self.assertTrue(hasattr(self.dns_client, 'domain'))
#        self.assertTrue(hasattr(self.dns_client, 'record'))
#
#    def test_list_zones(self):
#        zone_list = ['test']
#        self.client.__getitem__().getObject.return_value = {
#            'domains': zone_list}
#        zones = self.dns_client.list_zones()
#        self.assertEqual(zones, zone_list)
#
#    def test_get_zone(self):
#        zone_list = [
#            {'name': 'test-example.com'},
#            {'name': 'example.com'},
#        ]
#
#        # match
#        self.client.__getitem__().getByDomainName.return_value = \
#            zone_list
#        res = self.dns_client.get_zone('example.com')
#        self.assertEqual(res, zone_list[1])
#
#        # no match
#        from SoftLayer.DNS import DNSZoneNotFound
#        self.assertRaises(
#            DNSZoneNotFound,
#            self.dns_client.get_zone,
#            'shouldnt-match.com')
#
#    def test_create_zone(self):
#        self.client.__getitem__().createObject.return_value = \
#            {'name': 'example.com'}
#
#        res = self.dns_client.create_zone('example.com')
#        self.assertEqual(res, {'name': 'example.com'})
#
#    def test_delete_zone(self):
#        self.dns_client.delete_zone(1)
#        self.client.__getitem__().deleteObject.assert_called_once_with(id=1)
#
#    def test_edit_zone(self):
#        self.dns_client.edit_zone('example.com')
#        self.client.__getitem__().editObject.assert_called_once_with(
#            'example.com')
#
#    def test_create_record(self):
#        self.dns_client.create_record(1, 'test', 'TXT', 'testing', ttl=1200)
#
#        self.client.__getitem__().createObject.assert_called_once_with(
#            {
#                'domainId': 1,
#                'ttl': 1200,
#                'host': 'test',
#                'type': 'TXT',
#                'data': 'testing'
#            })
#
#    def test_delete_record(self):
#        self.dns_client.delete_record(1)
#        self.client.__getitem__().deleteObject.assert_called_once_with(id=1)
#
#    def test_search_record(self):
#        self.client.__getitem__().getByDomainName.return_value = [{
#            'name': 'example.com',
#            'resourceRecords': [
#                {'host': 'TEST1'},
#                {'host': 'test2'},
#                {'host': 'test3'},
#            ]
#        }]
#
#        res = self.dns_client.search_record('example.com', 'test1')
#        self.assertEqual(res, [{'host': 'TEST1'}])
#
#    def test_edit_record(self):
#        self.dns_client.edit_record({'id': 1, 'name': 'test'})
#        self.client.__getitem__().editObject.assert_called_once_with(
#            {'id': 1, 'name': 'test'},
#            id=1
#        )
#
#    def test_dump_zone(self):
#        self.client.__getitem__().getZoneFileContents.return_value = (
#            'lots of text')
#        self.dns_client.dump_zone(1)
#        self.client.__getitem__().getZoneFileContents.assert_called_once_with(
#            id=1)
