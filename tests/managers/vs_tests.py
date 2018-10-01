"""
    SoftLayer.tests.managers.vs_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.

"""
import mock

import SoftLayer
from SoftLayer import exceptions
from SoftLayer import fixtures
from SoftLayer import testing


class VSTests(testing.TestCase):

    def set_up(self):
        self.vs = SoftLayer.VSManager(self.client,
                                      SoftLayer.OrderingManager(self.client))

    def test_list_instances(self):
        results = self.vs.list_instances(hourly=True, monthly=True)

        for result in results:
            self.assertIn(result['id'], [100, 104])
        self.assert_called_with('SoftLayer_Account', 'getVirtualGuests')

    def test_list_instances_neither(self):
        results = self.vs.list_instances(hourly=False, monthly=False)

        for result in results:
            self.assertIn(result['id'], [100, 104])
        self.assert_called_with('SoftLayer_Account', 'getVirtualGuests')

    def test_list_instances_monthly(self):
        results = self.vs.list_instances(hourly=False, monthly=True)

        for result in results:
            self.assertIn(result['id'], [100])
        self.assert_called_with('SoftLayer_Account', 'getMonthlyVirtualGuests')

    def test_list_instances_hourly(self):
        results = self.vs.list_instances(hourly=True, monthly=False)

        for result in results:
            self.assertIn(result['id'], [104])
        self.assert_called_with('SoftLayer_Account', 'getHourlyVirtualGuests')

    def test_list_instances_with_filters(self):
        self.vs.list_instances(
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

        _filter = {
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
            }
        }
        self.assert_called_with('SoftLayer_Account', 'getVirtualGuests',
                                filter=_filter)

    def test_resolve_ids_ip(self):
        _id = self.vs._get_ids_from_ip('172.16.240.2')

        self.assertEqual(_id, [100, 104])

    def test_resolve_ids_ip_private(self):
        # Now simulate a private IP test
        mock = self.set_mock('SoftLayer_Account', 'getVirtualGuests')
        mock.side_effect = [[], [{'id': 99}]]

        _id = self.vs._get_ids_from_ip('10.0.1.87')

        self.assertEqual(_id, [99])

    def test_resolve_ids_ip_invalid(self):
        _id = self.vs._get_ids_from_ip('nope')
        self.assertEqual(_id, [])

    def test_resolve_ids_hostname(self):
        _id = self.vs._get_ids_from_hostname('vs-test1')
        self.assertEqual(_id, [100, 104])

    def test_get_instance(self):
        result = self.vs.get_instance(100)

        self.assertEqual(fixtures.SoftLayer_Virtual_Guest.getObject, result)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'getObject',
                                identifier=100)

    def test_get_create_options(self):
        results = self.vs.get_create_options()

        self.assertEqual(
            fixtures.SoftLayer_Virtual_Guest.getCreateObjectOptions, results)

    def test_cancel_instance(self):
        result = self.vs.cancel_instance(1)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'deleteObject',
                                identifier=1)

    def test_reload_instance(self):
        self.vs.reload_instance(1)

        self.assert_called_with('SoftLayer_Virtual_Guest',
                                'reloadOperatingSystem',
                                args=('FORCE', {}),
                                identifier=1)

    def test_reload_instance_posturi_sshkeys(self):
        post_uri = 'http://test.sftlyr.ws/test.sh'

        self.vs.reload_instance(1, post_uri=post_uri, ssh_keys=[1701])

        args = ('FORCE', {'customProvisionScriptUri': post_uri,
                          'sshKeyIds': [1701]})
        self.assert_called_with('SoftLayer_Virtual_Guest',
                                'reloadOperatingSystem',
                                args=args,
                                identifier=1)

    def test_reload_instance_with_new_os(self):
        self.vs.reload_instance(1, image_id=1234)

        args = ('FORCE', {'imageTemplateId': 1234})
        self.assert_called_with('SoftLayer_Virtual_Guest',
                                'reloadOperatingSystem',
                                args=args,
                                identifier=1)

    @mock.patch('SoftLayer.managers.vs.VSManager._generate_create_dict')
    def test_create_verify(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}

        self.vs.verify_create_instance(test=1, verify=1, tags=['test', 'tags'])

        create_dict.assert_called_once_with(test=1, verify=1)
        self.assert_called_with('SoftLayer_Virtual_Guest',
                                'generateOrderTemplate',
                                args=({'test': 1, 'verify': 1},))

    @mock.patch('SoftLayer.managers.vs.VSManager._generate_create_dict')
    def test_create_instance(self, create_dict):
        create_dict.return_value = {'test': 1, 'verify': 1}

        self.vs.create_instance(test=1, verify=1, tags='dev,green')

        create_dict.assert_called_once_with(test=1, verify=1)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'createObject',
                                args=({'test': 1, 'verify': 1},))
        self.assert_called_with('SoftLayer_Virtual_Guest', 'setTags',
                                args=('dev,green',),
                                identifier=100)

    def test_create_instances(self):
        self.vs.create_instances([{'cpus': 1,
                                   'memory': 1024,
                                   'hostname': 'server',
                                   'domain': 'example.com',
                                   'tags': 'dev,green'}])

        args = ([{'domain': 'example.com',
                  'hourlyBillingFlag': True,
                  'localDiskFlag': True,
                  'maxMemory': 1024,
                  'hostname': 'server',
                  'startCpus': 1,
                  'supplementalCreateObjectOptions': {'bootMode': None}}],)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'createObjects',
                                args=args)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'setTags',
                                args=('dev,green',),
                                identifier=100)

    def test_generate_os_and_image(self):
        self.assertRaises(
            ValueError,
            self.vs._generate_create_dict,
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code=1,
            image_id=1,
        )

    def test_generate_missing(self):
        self.assertRaises(ValueError, self.vs._generate_create_dict)
        self.assertRaises(ValueError, self.vs._generate_create_dict, cpus=1)

    def test_generate_basic(self):
        data = self.vs._generate_create_dict(
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
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_monthly(self):
        data = self.vs._generate_create_dict(
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
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_image_id(self):
        data = self.vs._generate_create_dict(
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
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_dedicated(self):
        data = self.vs._generate_create_dict(
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
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_datacenter(self):
        data = self.vs._generate_create_dict(
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
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_public_vlan(self):
        data = self.vs._generate_create_dict(
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
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_public_vlan_with_public_subnet(self):
        data = self.vs._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            public_vlan=1,
            public_subnet=1
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'primaryNetworkComponent': {'networkVlan': {'id': 1,
                                                        'primarySubnet': {'id': 1}}},
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_private_vlan_with_private_subnet(self):
        data = self.vs._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            private_vlan=1,
            private_subnet=1
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'primaryBackendNetworkComponent': {'networkVlan': {'id': 1,
                                                               'primarySubnet': {'id': 1}}},
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_private_vlan_subnet_public_vlan_subnet(self):
        data = self.vs._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            private_vlan=1,
            private_subnet=1,
            public_vlan=1,
            public_subnet=1,
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'primaryBackendNetworkComponent': {'networkVlan': {'id': 1,
                                                               'primarySubnet': {'id': 1}}},
            'primaryNetworkComponent': {'networkVlan': {'id': 1,
                                                        'primarySubnet': {'id': 1}}},
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_private_subnet(self):
        actual = self.assertRaises(
            exceptions.SoftLayerError,
            self.vs._generate_create_dict,
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            private_subnet=1,
        )

        self.assertEqual(str(actual), "You need to specify a private_vlan with private_subnet")

    def test_generate_public_subnet(self):
        actual = self.assertRaises(
            exceptions.SoftLayerError,
            self.vs._generate_create_dict,
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            public_subnet=1,
        )

        self.assertEqual(str(actual), "You need to specify a public_vlan with public_subnet")

    def test_generate_private_vlan(self):
        data = self.vs._generate_create_dict(
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
            'primaryBackendNetworkComponent': {'networkVlan': {'id': 1}},
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_create_network_components_vlan_subnet_private_vlan_subnet_public(self):
        data = self.vs._create_network_components(
            private_vlan=1,
            private_subnet=1,
            public_vlan=1,
            public_subnet=1,
        )

        assert_data = {
            'primaryBackendNetworkComponent': {'networkVlan': {'id': 1,
                                                               'primarySubnet': {'id': 1}}},
            'primaryNetworkComponent': {'networkVlan': {'id': 1,
                                                        'primarySubnet': {'id': 1}}},
        }

        self.assertEqual(data, assert_data)

    def test_create_network_components_vlan_subnet_private(self):
        data = self.vs._create_network_components(
            private_vlan=1,
            private_subnet=1,
        )

        assert_data = {
            'primaryBackendNetworkComponent': {'networkVlan': {'id': 1,
                                                               'primarySubnet': {'id': 1}}},
        }

        self.assertEqual(data, assert_data)

    def test_create_network_components_vlan_subnet_public(self):
        data = self.vs._create_network_components(
            public_vlan=1,
            public_subnet=1,
        )

        assert_data = {
            'primaryNetworkComponent': {'networkVlan': {'id': 1,
                                                        'primarySubnet': {'id': 1}}},
        }

        self.assertEqual(data, assert_data)

    def test_create_network_components_private_subnet(self):
        actual = self.assertRaises(
            exceptions.SoftLayerError,
            self.vs._create_network_components,
            private_subnet=1,
        )

        self.assertEqual(str(actual), "You need to specify a private_vlan with private_subnet")

    def test_create_network_components_public_subnet(self):
        actual = self.assertRaises(
            exceptions.SoftLayerError,
            self.vs._create_network_components,
            public_subnet=1,
        )

        self.assertEqual(str(actual), "You need to specify a public_vlan with public_subnet")

    def test_generate_userdata(self):
        data = self.vs._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            userdata="ICANHAZVSI",
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'userData': [{'value': "ICANHAZVSI"}],
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_network(self):
        data = self.vs._generate_create_dict(
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
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_private_network_only(self):
        data = self.vs._generate_create_dict(
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
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_post_uri(self):
        data = self.vs._generate_create_dict(
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
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_sshkey(self):
        data = self.vs._generate_create_dict(
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
            'supplementalCreateObjectOptions': {'bootMode': None},
        }

        self.assertEqual(data, assert_data)

    def test_generate_no_disks(self):
        data = self.vs._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING"
        )

        self.assertEqual(data.get('blockDevices'), None)

    def test_generate_single_disk(self):
        data = self.vs._generate_create_dict(
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
        data = self.vs._generate_create_dict(
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

    def test_generate_boot_mode(self):
        data = self.vs._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            boot_mode="HVM"
        )

        assert_data = {
            'startCpus': 1,
            'maxMemory': 1,
            'hostname': 'test',
            'domain': 'example.com',
            'localDiskFlag': True,
            'operatingSystemReferenceCode': "STRING",
            'hourlyBillingFlag': True,
            'supplementalCreateObjectOptions': {'bootMode': 'HVM'},
        }

        self.assertEqual(data, assert_data)

    def test_change_port_speed_public(self):
        result = self.vs.change_port_speed(1, True, 100)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Virtual_Guest',
                                'setPublicNetworkInterfaceSpeed',
                                identifier=1,
                                args=(100,))

    def test_change_port_speed_private(self):
        result = self.vs.change_port_speed(2, False, 10)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Virtual_Guest',
                                'setPrivateNetworkInterfaceSpeed',
                                identifier=2,
                                args=(10,))

    def test_rescue(self):
        # Test rescue environment
        result = self.vs.rescue(1234)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Virtual_Guest',
                                'executeRescueLayer',
                                identifier=1234)

    def test_edit_metadata(self):
        # Test editing user data
        result = self.vs.edit(100, userdata='my data')

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'setUserMetadata',
                                identifier=100,
                                args=(['my data'],))

    def test_edit_blank(self):
        # Now test a blank edit
        self.assertTrue(self.vs.edit, 100)

    def test_edit_full(self):
        result = self.vs.edit(100,
                              hostname='new-host',
                              domain='new.sftlyr.ws',
                              notes='random notes')

        self.assertEqual(result, True)
        args = ({
            'hostname': 'new-host',
            'domain': 'new.sftlyr.ws',
            'notes': 'random notes',
        },)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'editObject',
                                identifier=100,
                                args=args)

    def test_edit_tags(self):
        # Test tag support
        result = self.vs.edit(100, tags='dev,green')

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'setTags',
                                identifier=100,
                                args=('dev,green',))

    def test_edit_tags_blank(self):
        result = self.vs.edit(100, tags='')

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'setTags',
                                identifier=100,
                                args=('',))

    def test_captures(self):
        # capture only the OS disk
        result = self.vs.capture(1, 'a')

        expected = fixtures.SoftLayer_Virtual_Guest.createArchiveTransaction
        self.assertEqual(result, expected)
        args = ('a', [{'device': 0, 'uuid': 1, 'mountType': 'Disk'}], None)
        self.assert_called_with('SoftLayer_Virtual_Guest',
                                'createArchiveTransaction',
                                args=args,
                                identifier=1)

    def test_capture_additional_disks(self):
        # capture all the disks, minus the swap
        # make sure the data is carried along with it
        result = self.vs.capture(1, 'a', additional_disks=True)

        expected = fixtures.SoftLayer_Virtual_Guest.createArchiveTransaction
        self.assertEqual(result, expected)
        args = ('a', [{'device': 0, 'mountType': 'Disk', 'uuid': 1},
                      {'device': 3, 'mountType': 'Disk', 'uuid': 3}], None)
        self.assert_called_with('SoftLayer_Virtual_Guest',
                                'createArchiveTransaction',
                                args=args,
                                identifier=1)

    def test_upgrade(self):
        # test single upgrade
        result = self.vs.upgrade(1, cpus=4, public=False)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(order_container['prices'], [{'id': 1007}])
        self.assertEqual(order_container['virtualGuests'], [{'id': 1}])

    def test_upgrade_blank(self):
        # Now test a blank upgrade
        result = self.vs.upgrade(1)

        self.assertEqual(result, False)
        self.assertEqual(self.calls('SoftLayer_Product_Order', 'placeOrder'),
                         [])

    def test_upgrade_full(self):
        # Testing all parameters Upgrade
        result = self.vs.upgrade(1,
                                 cpus=4,
                                 memory=2,
                                 nic_speed=1000,
                                 public=True)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertIn({'id': 1144}, order_container['prices'])
        self.assertIn({'id': 1133}, order_container['prices'])
        self.assertIn({'id': 1122}, order_container['prices'])
        self.assertEqual(order_container['virtualGuests'], [{'id': 1}])

    def test_upgrade_with_flavor(self):
        # Testing Upgrade with parameter preset
        result = self.vs.upgrade(1,
                                 preset="M1_64X512X100",
                                 nic_speed=1000,
                                 public=True)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(799, order_container['presetId'])
        self.assertIn({'id': 1}, order_container['virtualGuests'])
        self.assertIn({'id': 1122}, order_container['prices'])
        self.assertEqual(order_container['virtualGuests'], [{'id': 1}])

    def test_upgrade_dedicated_host_instance(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getUpgradeItemPrices')
        mock.return_value = fixtures.SoftLayer_Virtual_Guest.DEDICATED_GET_UPGRADE_ITEM_PRICES

        # test single upgrade
        result = self.vs.upgrade(1, cpus=4, public=False)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder')
        call = self.calls('SoftLayer_Product_Order', 'placeOrder')[0]
        order_container = call.args[0]
        self.assertEqual(order_container['prices'], [{'id': 115566}])
        self.assertEqual(order_container['virtualGuests'], [{'id': 1}])

    def test_get_item_id_for_upgrade(self):
        item_id = 0
        package_items = self.client['Product_Package'].getItems(id=46)
        for item in package_items:
            if ((item['prices'][0]['categories'][0]['id'] == 3)
                    and (item.get('capacity') == '2')):
                item_id = item['prices'][0]['id']
                break
        self.assertEqual(1133, item_id)

    def test_get_package_items(self):
        self.vs._get_package_items()
        self.assert_called_with('SoftLayer_Product_Package', 'getItems')

    def test_get_price_id_for_upgrade(self):
        package_items = self.vs._get_package_items()

        price_id = self.vs._get_price_id_for_upgrade(package_items=package_items,
                                                     option='cpus',
                                                     value='4')
        self.assertEqual(1144, price_id)

    def test_get_price_id_for_upgrade_skips_location_price(self):
        package_items = self.vs._get_package_items()

        price_id = self.vs._get_price_id_for_upgrade(package_items=package_items,
                                                     option='cpus',
                                                     value='55')
        self.assertEqual(None, price_id)

    def test_get_price_id_for_upgrade_finds_nic_price(self):
        package_items = self.vs._get_package_items()

        price_id = self.vs._get_price_id_for_upgrade(package_items=package_items,
                                                     option='memory',
                                                     value='2')
        self.assertEqual(1133, price_id)

    def test_get_price_id_for_upgrade_finds_memory_price(self):
        package_items = self.vs._get_package_items()

        price_id = self.vs._get_price_id_for_upgrade(package_items=package_items,
                                                     option='nic_speed',
                                                     value='1000')
        self.assertEqual(1122, price_id)


class VSWaitReadyGoTests(testing.TestCase):

    def set_up(self):
        self.client = mock.MagicMock()
        self.vs = SoftLayer.VSManager(self.client)
        self.guestObject = self.client['Virtual_Guest'].getObject

    @mock.patch('SoftLayer.managers.vs.VSManager.wait_for_ready')
    def test_wait_interface(self, ready):
        # verify interface to wait_for_ready is intact
        self.vs.wait_for_transaction(1, 1)
        ready.assert_called_once_with(1, 1, delay=10, pending=True)

    def test_active_not_provisioned(self):
        # active transaction and no provision date should be false
        self.guestObject.return_value = {'activeTransaction': {'id': 1}}
        value = self.vs.wait_for_ready(1, 0)
        self.assertFalse(value)

    def test_active_and_provisiondate(self):
        # active transaction and provision date should be True
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1},
             'provisionDate': 'aaa'},
        ]
        value = self.vs.wait_for_ready(1, 1)
        self.assertTrue(value)

    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_active_provision_pending(self, _now, _sleep):
        _now.side_effect = [0, 0, 1, 1, 2, 2]
        # active transaction and provision date
        # and pending should be false
        self.guestObject.return_value = {'activeTransaction': {'id': 2}, 'provisionDate': 'aaa'}

        value = self.vs.wait_for_ready(instance_id=1, limit=1, delay=1, pending=True)
        _sleep.assert_has_calls([mock.call(0)])
        self.assertFalse(value)

    def test_reload_no_pending(self):
        # reload complete, maintance transactions
        self.guestObject.return_value = {
            'activeTransaction': {'id': 2},
            'provisionDate': 'aaa',
            'lastOperatingSystemReload': {'id': 1},
        }

        value = self.vs.wait_for_ready(1, 1)
        self.assertTrue(value)

    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_reload_pending(self, _now, _sleep):
        _now.side_effect = [0, 0, 1, 1, 2, 2]
        # reload complete, pending maintance transactions
        self.guestObject.return_value = {'activeTransaction': {'id': 2},
                                         'provisionDate': 'aaa',
                                         'lastOperatingSystemReload': {'id': 1}}
        value = self.vs.wait_for_ready(instance_id=1, limit=1, delay=1, pending=True)
        _sleep.assert_has_calls([mock.call(0)])
        self.assertFalse(value)

    @mock.patch('time.sleep')
    def test_ready_iter_once_incomplete(self, _sleep):
        # no iteration, false
        self.guestObject.return_value = {'activeTransaction': {'id': 1}}
        value = self.vs.wait_for_ready(1, 0, delay=1)
        self.assertFalse(value)
        _sleep.assert_has_calls([mock.call(0)])

    @mock.patch('time.sleep')
    def test_iter_once_complete(self, _sleep):
        # no iteration, true
        self.guestObject.return_value = {'provisionDate': 'aaa'}
        value = self.vs.wait_for_ready(1, 1, delay=1)
        self.assertTrue(value)
        self.assertFalse(_sleep.called)

    @mock.patch('time.sleep')
    def test_iter_four_complete(self, _sleep):
        # test 4 iterations with positive match
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'provisionDate': 'aaa'},
        ]

        value = self.vs.wait_for_ready(1, 4, delay=1)
        self.assertTrue(value)
        _sleep.assert_has_calls([mock.call(1), mock.call(1), mock.call(1)])
        self.guestObject.assert_has_calls([
            mock.call(id=1, mask=mock.ANY), mock.call(id=1, mask=mock.ANY),
            mock.call(id=1, mask=mock.ANY), mock.call(id=1, mask=mock.ANY),
        ])

    @mock.patch('time.time')
    @mock.patch('time.sleep')
    def test_iter_two_incomplete(self, _sleep, _time):
        # test 2 iterations, with no matches
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'provisionDate': 'aaa'}
        ]
        # logging calls time.time as of pytest3.3, not sure if there is a better way of getting around that.
        _time.side_effect = [0, 1, 2, 3, 4, 5, 6]
        value = self.vs.wait_for_ready(1, 2, delay=1)
        self.assertFalse(value)
        _sleep.assert_has_calls([mock.call(1), mock.call(0)])
        self.guestObject.assert_has_calls([
            mock.call(id=1, mask=mock.ANY),
            mock.call(id=1, mask=mock.ANY),
        ])

    @mock.patch('time.time')
    @mock.patch('time.sleep')
    def test_iter_20_incomplete(self, _sleep, _time):
        """Wait for up to 20 seconds (sleeping for 10 seconds) for a server."""
        self.guestObject.return_value = {'activeTransaction': {'id': 1}}
        # logging calls time.time as of pytest3.3, not sure if there is a better way of getting around that.
        _time.side_effect = [0, 0, 10, 10, 20, 20, 50, 60]
        value = self.vs.wait_for_ready(1, 20, delay=10)
        self.assertFalse(value)
        self.guestObject.assert_has_calls([mock.call(id=1, mask=mock.ANY)])

        _sleep.assert_has_calls([mock.call(10)])

    @mock.patch('SoftLayer.decoration.sleep')
    @mock.patch('SoftLayer.transports.FixtureTransport.__call__')
    @mock.patch('time.time')
    @mock.patch('time.sleep')
    def test_exception_from_api(self, _sleep, _time, _vs, _dsleep):
        """Tests escalating scale back when an excaption is thrown"""
        _dsleep.return_value = False

        self.guestObject.side_effect = [
            exceptions.TransportError(104, "Its broken"),
            {'activeTransaction': {'id': 1}},
            {'provisionDate': 'aaa'}
        ]
        # logging calls time.time as of pytest3.3, not sure if there is a better way of getting around that.
        _time.side_effect = [0, 1, 2, 3, 4]
        value = self.vs.wait_for_ready(1, 20, delay=1)
        _sleep.assert_called_once()
        _dsleep.assert_called_once()
        self.assertTrue(value)
