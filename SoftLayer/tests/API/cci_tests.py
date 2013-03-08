import SoftLayer
import SoftLayer.CCI

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA
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
        self.assertRaises(
            SoftLayer.CCI.CCICreateMissingRequired,
            self.cci._generate_create_dict,
            cpus=1
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
            'hourlyBillingFlag': False,
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
            'primaryNetworkComponent': {"networkVlan": {"id": 1}},
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
            'primaryBackendNetworkComponent': {"networkVlan": {"id": 1}},
        }

        self.assertEqual(data, assert_data)

    def test_generate_userdata(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            userdata="ICANHAZCCI",
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'userData': [{'value': "ICANHAZCCI"}],
        }

        self.assertEqual(data, assert_data)

    def test_generate_network(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            nic_speed=9001,
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'networkComponents': [{'maxSpeed': 9001}],
        }

        self.assertEqual(data, assert_data)
