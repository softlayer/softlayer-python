"""
    SoftLayer.tests.managers.cci_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import CCIManager
from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.tests.fixtures import Virtual_Guest

from mock import MagicMock, ANY, call, patch


class CCITests(unittest.TestCase):

    def setUp(self):
        self.client = FixtureClient()
        self.cci = CCIManager(self.client)

    def test_list_instances(self):
        mcall = call(mask=ANY, filter={})
        service = self.client['Account']

        list_expected_ids = [100, 104]
        hourly_expected_ids = [104]
        monthly_expected_ids = [100]

        results = self.cci.list_instances(hourly=True, monthly=True)
        service.getVirtualGuests.assert_has_calls(mcall)
        for result in results:
            self.assertIn(result['id'], list_expected_ids)

        result = self.cci.list_instances(hourly=False, monthly=False)
        service.getVirtualGuests.assert_has_calls(mcall)
        for result in results:
            self.assertIn(result['id'], list_expected_ids)

        results = self.cci.list_instances(hourly=False, monthly=True)
        service.getMonthlyVirtualGuests.assert_has_calls(mcall)
        for result in results:
            self.assertIn(result['id'], monthly_expected_ids)

        results = self.cci.list_instances(hourly=True, monthly=False)
        service.getHourlyVirtualGuests.assert_has_calls(mcall)
        for result in results:
            self.assertIn(result['id'], hourly_expected_ids)

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

        service = self.client['Account']
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
        service = self.client['Account']
        _id = self.cci._get_ids_from_ip('172.16.240.2')
        self.assertEqual(_id, [100, 104])

        _id = self.cci._get_ids_from_ip('nope')
        self.assertEqual(_id, [])

        # Now simulate a private IP test
        service.getVirtualGuests.side_effect = [[], [{'id': 99}]]
        _id = self.cci._get_ids_from_ip('10.0.1.87')
        self.assertEqual(_id, [99])

    def test_resolve_ids_hostname(self):
        _id = self.cci._get_ids_from_hostname('cci-test1')
        self.assertEqual(_id, [100, 104])

    def test_get_instance(self):
        result = self.cci.get_instance(100)
        self.client['Virtual_Guest'].getObject.assert_called_once_with(
            id=100, mask=ANY)
        self.assertEqual(Virtual_Guest.getObject, result)

    def test_get_create_options(self):
        results = self.cci.get_create_options()
        self.assertEqual(Virtual_Guest.getCreateObjectOptions, results)

    def test_cancel_instance(self):
        self.cci.cancel_instance(1)
        self.client['Virtual_Guest'].deleteObject.assert_called_once_with(id=1)

    def test_reload_instance(self):
        post_uri = 'http://test.sftlyr.ws/test.sh'
        self.cci.reload_instance(1, post_uri=post_uri, ssh_keys=[1701])
        service = self.client['Virtual_Guest']
        f = service.reloadOperatingSystem
        f.assert_called_once_with('FORCE',
                                  {'customProvisionScriptUri': post_uri,
                                   'sshKeyIds': [1701]}, id=1)

    @patch('SoftLayer.managers.cci.CCIManager._generate_create_dict')
    def test_create_verify(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        self.cci.verify_create_instance(test=1, verify=1)
        create_dict.assert_called_once_with(test=1, verify=1)
        f = self.client['Virtual_Guest'].generateOrderTemplate
        f.assert_called_once_with({'test': 1, 'verify': 1})

    @patch('SoftLayer.managers.cci.CCIManager._generate_create_dict')
    def test_create_instance(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}
        self.cci.create_instance(test=1, verify=1)
        create_dict.assert_called_once_with(test=1, verify=1)
        self.client['Virtual_Guest'].createObject.assert_called_once_with(
            {'test': 1, 'verify': 1})

    def test_generate_os_and_image(self):
        self.assertRaises(
            ValueError,
            self.cci._generate_create_dict,
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code=1,
            image_id=1,
        )

    def test_generate_missing(self):
        self.assertRaises(ValueError, self.cci._generate_create_dict)
        self.assertRaises(ValueError, self.cci._generate_create_dict, cpus=1)

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

    def test_generate_dedicated(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            dedicated=True,
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

    def test_generate_private_network_only(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            nic_speed=9001,
            private=True
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'privateNetworkOnlyFlag': True,
            'hourlyBillingFlag': True,
            'networkComponents': [{'maxSpeed': 9001}],
        }

        self.assertEqual(data, assert_data)

    def test_generate_post_uri(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            post_uri='https://example.com/boostrap.sh',
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'postInstallScriptUri': 'https://example.com/boostrap.sh',
        }

        self.assertEqual(data, assert_data)

    def test_generate_sshkey(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            ssh_keys=[543],
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'sshKeys': [{'id': 543}],
        }

        self.assertEqual(data, assert_data)

    def test_generate_no_disks(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING"
        )

        self.assertEqual(data.get('blockDevices'), None)

    def test_generate_single_disk(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            disks=[50]
        )

        assert_data = {
            'blockDevices': [
                {"device": "0", "diskImage": {"capacity": 50}}]
        }

        self.assertTrue(data.get('blockDevices'))
        self.assertEqual(data['blockDevices'], assert_data['blockDevices'])

    def test_generate_multi_disk(self):
        data = self.cci._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            disks=[50, 70, 100]
        )

        assert_data = {
            'blockDevices': [
                {"device": "0", "diskImage": {"capacity": 50}},
                {"device": "2", "diskImage": {"capacity": 70}},
                {"device": "3", "diskImage": {"capacity": 100}}]
        }

        self.assertTrue(data.get('blockDevices'))
        self.assertEqual(data['blockDevices'], assert_data['blockDevices'])

    def test_change_port_speed_public(self):
        cci_id = 1
        speed = 100
        self.cci.change_port_speed(cci_id, True, speed)

        service = self.client['Virtual_Guest']
        f = service.setPublicNetworkInterfaceSpeed
        f.assert_called_once_with(speed, id=cci_id)

    def test_change_port_speed_private(self):
        cci_id = 2
        speed = 10
        self.cci.change_port_speed(cci_id, False, speed)

        service = self.client['Virtual_Guest']
        f = service.setPrivateNetworkInterfaceSpeed
        f.assert_called_once_with(speed, id=cci_id)

    def test_edit(self):
        # Test editing user data
        service = self.client['Virtual_Guest']

        self.cci.edit(100, userdata='my data')

        service.setUserMetadata.assert_called_once_with(['my data'], id=100)

        # Now test a blank edit
        self.assertTrue(self.cci.edit, 100)

        # Finally, test a full edit
        args = {
            'hostname': 'new-host',
            'domain': 'new.sftlyr.ws',
            'notes': 'random notes',
        }

        self.cci.edit(100, **args)
        service.editObject.assert_called_once_with(args, id=100)

    def test_captures(self):
        archive = self.client['Virtual_Guest'].createArchiveTransaction
        getObject = self.client['Virtual_Guest'].getObject
        getObject.side_effect = {
            'blockDevices': [
                {"device": 0, "uuid": 1},
                {"device": 1},
                {"device": 2, "uuid": 2},
            ]
        }

        # capture only the OS disk
        self.cci.capture(1, 'a')
        archive.called_once_with('a', [{"device": 0}], "", id=1)

        archive.reset()

        # capture all the disks, minus the swap
        # make sure the data is carried along with it
        self.cci.capture(1, 'a', additional_disks=True)
        archive.called_once_with('a', [{"device": 0, "uuid": 1},
                                 {"device": 2, "uuid": 2}], "", id=1)


class CCIWaitReadyGoTests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.cci = CCIManager(self.client)
        self.guestObject = self.client['Virtual_Guest'].getObject

    @patch('SoftLayer.managers.cci.CCIManager.wait_for_ready')
    def test_wait_interface(self, ready):
        # verify interface to wait_for_ready is intact
        self.cci.wait_for_transaction(1, 1)
        ready.assert_called_once_with(1, 1, delay=1, pending=True)

    def test_active_not_provisioned(self):
        # active transaction and no provision date should be false
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1}},
        ]
        value = self.cci.wait_for_ready(1, 1)
        self.assertFalse(value)

    def test_active_and_provisiondate(self):
        # active transaction and provision date should be True
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1},
             'provisionDate': 'aaa'},
        ]
        value = self.cci.wait_for_ready(1, 1)
        self.assertTrue(value)

    def test_active_provision_pending(self):
        # active transaction and provision date
        # and pending should be false
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1},
             'provisionDate': 'aaa'},
        ]
        value = self.cci.wait_for_ready(1, 1, pending=True)
        self.assertFalse(value)

    def test_active_reload(self):
        # actively running reload
        self.guestObject.side_effect = [
            {
                'activeTransaction': {'id': 1},
                'provisionDate': 'aaa',
                'lastOperatingSystemReload': {'id': 1},
            },
        ]
        value = self.cci.wait_for_ready(1, 1)
        self.assertFalse(value)

    def test_reload_no_pending(self):
        # reload complete, maintance transactions
        self.guestObject.side_effect = [
            {
                'activeTransaction': {'id': 2},
                'provisionDate': 'aaa',
                'lastOperatingSystemReload': {'id': 1},
            },
        ]
        value = self.cci.wait_for_ready(1, 1)
        self.assertTrue(value)

    def test_reload_pending(self):
        # reload complete, pending maintance transactions
        self.guestObject.side_effect = [
            {
                'activeTransaction': {'id': 2},
                'provisionDate': 'aaa',
                'lastOperatingSystemReload': {'id': 1},
            },
        ]
        value = self.cci.wait_for_ready(1, 1, pending=True)
        self.assertFalse(value)

    @patch('SoftLayer.managers.cci.sleep')
    def test_ready_iter_once_incomplete(self, _sleep):
        self.guestObject = self.client['Virtual_Guest'].getObject

        # no iteration, false
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1}},
        ]
        value = self.cci.wait_for_ready(1, 1)
        self.assertFalse(value)
        self.assertFalse(_sleep.called)

    @patch('SoftLayer.managers.cci.sleep')
    def test_iter_once_complete(self, _sleep):
        # no iteration, true
        self.guestObject.side_effect = [
            {'provisionDate': 'aaa'},
        ]
        value = self.cci.wait_for_ready(1, 1)
        self.assertTrue(value)
        self.assertFalse(_sleep.called)

    @patch('SoftLayer.managers.cci.sleep')
    def test_iter_four_complete(self, _sleep):
        # test 4 iterations with positive match
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'provisionDate': 'aaa'},
        ]

        value = self.cci.wait_for_ready(1, 4)
        self.assertTrue(value)
        _sleep.assert_has_calls([call(1), call(1), call(1)])
        self.guestObject.assert_has_calls([
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY), call(id=1, mask=ANY),
        ])

    @patch('SoftLayer.managers.cci.sleep')
    def test_iter_two_incomplete(self, _sleep):
        # test 2 iterations, with no matches
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'provisionDate': 'aaa'}
        ]
        value = self.cci.wait_for_ready(1, 2)
        self.assertFalse(value)
        _sleep.assert_called_once_with(1)
        self.guestObject.assert_has_calls([
            call(id=1, mask=ANY), call(id=1, mask=ANY),
        ])

    @patch('SoftLayer.managers.cci.sleep')
    def test_iter_ten_incomplete(self, _sleep):
        # 10 iterations at 10 second sleeps with no
        # matching values.
        self.guestObject.side_effect = [
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
        ]
        value = self.cci.wait_for_ready(1, 10, delay=10)
        self.assertFalse(value)
        self.guestObject.assert_has_calls([
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY), call(id=1, mask=ANY),
            call(id=1, mask=ANY), call(id=1, mask=ANY),
        ])
        # should only be 9 calls to sleep, last iteration
        # should return a value and skip the sleep
        _sleep.assert_has_calls([
            call(10), call(10), call(10), call(10), call(10),
            call(10), call(10), call(10), call(10)])
