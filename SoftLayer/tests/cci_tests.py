import SoftLayer

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from mock import MagicMock


class CCITests_unittests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.cci = SoftLayer.CCIManager(self.client)

    def test_list_instances(self):
        self.client.__getitem__().getObject.return_value = {
            'virtualGuests': "this is unique"}
        result = self.cci.list_instances()
        self.assertEqual(result, "this is unique")

        self.client.__getitem__().getObject.return_value = {
            'hourlyVirtualGuests': "this is unique"}
        result = self.cci.list_instances(restrict='hourlyVirtualGuests')
        self.assertEqual(result, "this is unique")

        self.client.__getitem__().getObject.return_value = {
            'monthlyVirtualGuests': "this is unique"}
        result = self.cci.list_instances(restrict='monthlyVirtualGuests')
        self.assertEqual(result, "this is unique")

    def test_get_instance(self):
        self.client.__getitem__().getObject.return_value = {
            'hourlyVirtualGuests': "this is unique"}
        result = self.cci.get_instance(1)
        self.client.__getitem__().getObject.assert_called_once_with(
            id=1)

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
