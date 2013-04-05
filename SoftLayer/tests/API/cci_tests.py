"""
    SoftLayer.tests.API.cci_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
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
        mcall = call(mask=ANY, filter={})
        service = self.client.__getitem__()

        self.cci.list_instances(hourly=True, monthly=True)
        service.getVirtualGuests.assert_has_calls(mcall)

        self.cci.list_instances(hourly=False, monthly=False)
        service.getVirtualGuests.assert_has_calls(mcall)

        self.cci.list_instances(hourly=False, monthly=True)
        service.getMonthlyVirtualGuests.assert_has_calls(mcall)

        self.cci.list_instances(hourly=True, monthly=False)
        service.getHourlyVirtualGuests.assert_has_calls(mcall)

    def test_list_instances_with_filters(self):
        self.cci.list_instances(
            hourly=True,
            monthly=True,
            tags=['tag1', 'tag2'],
            cpus=2,
            memory=1024,
            hostname='hostname',
            domain='example.com',
            local_disk=True,
            datacenter='dal05',
            nic_speed=100,
            public_ip='1.2.3.4',
            private_ip='4.3.2.1',
        )

        service = self.client.__getitem__()
        service.getVirtualGuests.assert_has_calls(call(
            filter={
                'virtualGuests': {
                    'datacenter': {
                        'name': {'operation': '_= dal05'}},
                    'domain': {'operation': '_= example.com'},
                    'tagReferences': {
                        'tag': {'name': {
                            'operation': 'in',
                            'options': [{
                                'name': 'data', 'value': ['tag1', 'tag2']}]}}},
                    'maxCpu': {'operation': 2},
                    'localDiskFlag': {'operation': True},
                    'maxMemory': {'operation': 1024},
                    'hostname': {'operation': '_= hostname'},
                    'networkComponents': {'maxSpeed': {'operation': 100}},
                    'primaryIpAddress': {'operation': '_= 1.2.3.4'},
                    'primaryBackendIpAddress': {'operation': '_= 4.3.2.1'}
                }},
            mask=ANY,
        ))

    def test_resolve_ids_ip(self):
        self.client.__getitem__().getVirtualGuests.return_value = \
            [{'id': '1234'}]
        _id = self.cci._get_ids_from_ip('1.2.3.4')
        self.assertEqual(_id, ['1234'])

        self.client.__getitem__().getVirtualGuests.side_effect = \
            [[], [{'id': '4321'}]]
        _id = self.cci._get_ids_from_ip('4.3.2.1')
        self.assertEqual(_id, ['4321'])

        _id = self.cci._get_ids_from_ip('nope')
        self.assertEqual(_id, [])

    def test_resolve_ids_hostname(self):
        self.client.__getitem__().getVirtualGuests.return_value = \
            [{'id': '1234'}]
        _id = self.cci._get_ids_from_hostname('hostname')
        self.assertEqual(_id, ['1234'])

    def test_get_instance(self):
        self.client.__getitem__().getObject.return_value = {
            'hourlyVirtualGuests': "this is unique"}
        self.cci.get_instance(1)
        self.client.__getitem__().getObject.assert_called_once_with(
            id=1, mask=ANY)

    def test_get_create_options(self):
        self.cci.get_create_options()
        f = self.client.__getitem__().getCreateObjectOptions
        f.assert_called_once_with()

    def test_cancel_instance(self):
        self.cci.cancel_instance(id=1)
        self.client.__getitem__().deleteObject.assert_called_once_with(id=1)

    def test_reload_instance(self):
        self.cci.reload_instance(id=1)
        f = self.client.__getitem__().reloadCurrentOperatingSystemConfiguration
        f.assert_called_once_with(id=1)

    @patch('SoftLayer.CCI.CCIManager._generate_create_dict')
    def test_create_verify(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        self.cci.verify_create_instance(test=1, verify=1)
        create_dict.assert_called_once_with(test=1, verify=1)
        f = self.client.__getitem__().generateOrderTemplate
        f.assert_called_once_with({'test': 1, 'verify': 1})

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

    @patch('SoftLayer.CCI.sleep')
    def test_wait(self, _sleep):
        guestObject = self.client.__getitem__().getObject

        # test 4 iterations with positive match
        guestObject.side_effect = [
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'provisionDate': 'aaa'},
            {'provisionDate': 'aaa'}
        ]

        value = self.cci.wait_for_transaction(1, 4)
        self.assertTrue(value)
        _sleep.assert_has_calls([call(1), call(1), call(1)])
        guestObject.assert_has_calls([
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY), call(id=1, mask=ANY),
        ])

        # test 2 iterations, with no matches
        _sleep.reset_mock()
        guestObject.reset_mock()

        guestObject.side_effect = [
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'provisionDate': 'aaa'}
        ]
        value = self.cci.wait_for_transaction(1, 2)
        self.assertFalse(value)
        _sleep.assert_has_calls([call(1), call(1)])
        guestObject.assert_has_calls([
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY)
        ])

        # 10 iterations at 10 second sleeps with no
        # matching values.
        _sleep.reset_mock()
        guestObject.reset_mock()
        guestObject.side_effect = [
            {},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}}
        ]
        value = self.cci.wait_for_transaction(1, 10, 10)
        self.assertFalse(value)
        guestObject.assert_has_calls([
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY)
        ])
        _sleep.assert_has_calls([
            call(10), call(10), call(10), call(10), call(10),
            call(10), call(10), call(10), call(10), call(10)])
