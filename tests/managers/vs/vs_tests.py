"""
    SoftLayer.tests.managers.vs.vs_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.

"""
from unittest import mock as mock

import SoftLayer
from SoftLayer import exceptions
from SoftLayer import fixtures
from SoftLayer import testing


class VSTests(testing.TestCase):

    def set_up(self):
        self.vs = SoftLayer.VSManager(self.client, SoftLayer.OrderingManager(self.client))

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
            transient=False,
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
                'primaryBackendIpAddress': {'operation': '_= 4.3.2.1'},
                'transientGuestFlag': {'operation': False},
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
        options = self.vs.get_create_options()

        extras = {'key': '1_IPV6_ADDRESS', 'name': '1 IPv6 Address'}
        locations = {'key': 'wdc07', 'name': 'Washington 7'}
        operating_systems = {
            'key': 'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
            'name': 'Ubuntu / 14.04-64',
            'referenceCode': 'UBUNTU_14_64'
        }

        port_speeds = {
            'key': '10',
            'name': '10 Mbps Public & Private Network Uplinks'
        }
        sizes = {
            'key': 'M1_64X512X25',
            'name': 'M1.64x512x25',
            'hourlyRecurringFee': 0.0,
            'recurringFee': 0.0
        }

        self.assertEqual(options['extras'][0]['key'], extras['key'])
        self.assertEqual(options['locations'][0], locations)
        self.assertEqual(options['operating_systems'][0]['referenceCode'],
                         operating_systems['referenceCode'])
        self.assertEqual(options['port_speed'][0]['name'], port_speeds['name'])
        self.assertEqual(options['sizes'][0], sizes)

    def test_get_create_options_prices_by_location(self):
        options = self.vs.get_create_options('wdc07')

        extras = {'key': '1_IPV6_ADDRESS', 'name': '1 IPv6 Address',
                  'prices': [
                      {
                          'hourlyRecurringFee': '0',
                          'id': 272,
                          'locationGroupId': '',
                          'recurringFee': '0',
                      }
                  ]
                  }
        locations = {'key': 'wdc07', 'name': 'Washington 7'}
        operating_systems = {
            'key': 'OS_UBUNTU_14_04_LTS_TRUSTY_TAHR_64_BIT',
            'name': 'Ubuntu / 14.04-64',
            'referenceCode': 'UBUNTU_14_64',
            'prices': [
                {
                    'hourlyRecurringFee': '0',
                    'id': 272,
                    'locationGroupId': '',
                    'recurringFee': '0',
                }
            ]
        }

        port_speeds = {
            'key': '10',
            'name': '10 Mbps Public & Private Network Uplinks',
            'prices': [
                {
                    'hourlyRecurringFee': '0',
                    'id': 272,
                    'locationGroupId': '',
                    'recurringFee': '0',
                }
            ]
        }
        sizes = {
            'key': 'M1_64X512X25',
            'name': 'M1.64x512x25',
            'hourlyRecurringFee': 0.0,
            'recurringFee': 0.0
        }

        self.assertEqual(options['extras'][0]['prices'][0]['hourlyRecurringFee'],
                         extras['prices'][0]['hourlyRecurringFee'])
        self.assertEqual(options['locations'][0], locations)
        self.assertEqual(options['operating_systems'][0]['prices'][0]['locationGroupId'],
                         operating_systems['prices'][0]['locationGroupId'])
        self.assertEqual(options['port_speed'][0]['prices'][0]['id'], port_speeds['prices'][0]['id'])
        self.assertEqual(options['sizes'][0], sizes)

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

    def test_generate_by_router_and_vlan(self):
        actual = self.assertRaises(
            exceptions.SoftLayerError,
            self.vs._generate_create_dict,
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            private_router=1,
            private_vlan=1
        )

        self.assertEqual(str(actual), "You have to select network vlan or network vlan with a subnet or only router, "
                                      "not all options")

    def test_generate_by_router_and_subnet(self):
        actual = self.assertRaises(
            exceptions.SoftLayerError,
            self.vs._generate_create_dict,
            cpus=1,
            memory=1,
            hostname='test',
            domain='example.com',
            os_code="STRING",
            private_router=1,
            private_subnet=1
        )

        self.assertEqual(str(actual), "You have to select network vlan or network vlan with a subnet or only router, "
                                      "not all options")

    def test_generate_sec_group(self):
        data = self.vs._generate_create_dict(
            cpus=1,
            memory=1,
            hostname='test',
            domain='test.com',
            os_code="OS",
            public_security_groups=[1, 2, 3],
            private_security_groups=[4, 5, 6]
        )

        pub_sec_binding = data['primaryNetworkComponent']['securityGroupBindings']
        prv_sec_binding = data['primaryBackendNetworkComponent']['securityGroupBindings']
        # Public
        self.assertEqual(pub_sec_binding[0]['securityGroup']['id'], 1)
        self.assertEqual(pub_sec_binding[1]['securityGroup']['id'], 2)
        self.assertEqual(pub_sec_binding[2]['securityGroup']['id'], 3)
        # Private
        self.assertEqual(prv_sec_binding[0]['securityGroup']['id'], 4)
        self.assertEqual(prv_sec_binding[1]['securityGroup']['id'], 5)
        self.assertEqual(prv_sec_binding[2]['securityGroup']['id'], 6)

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

    def test_create_network_components_by_routers(self):
        data = self.vs._create_network_components(
            private_router=1,
            public_router=1
        )

        assert_data = {
            'primaryBackendNetworkComponent': {'router': {'id': 1}},
            'primaryNetworkComponent': {'router': {'id': 1}},
        }

        self.assertEqual(data, assert_data)

    def test_create_network_components_by_routers_and_vlan(self):
        actual = self.assertRaises(
            exceptions.SoftLayerError,
            self.vs._create_network_components,
            private_router=1,
            public_router=1,
            private_vlan=1
        )

        self.assertEqual(str(actual), "You have to select network vlan or network vlan with a subnet or only router, "
                                      "not all options")

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

    def test_usage_vs_cpu(self):
        result = self.vs.get_summary_data_usage('100',
                                                start_date='2019-3-4',
                                                end_date='2019-4-2',
                                                valid_type='CPU0',
                                                summary_period=300)

        expected = fixtures.SoftLayer_Metric_Tracking_Object.getSummaryData
        self.assertEqual(result, expected)

        args = ('2019-3-4', '2019-4-2', [{"keyName": "CPU0", "summaryType": "max"}], 300)

        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getSummaryData', args=args, identifier=1000)

    def test_usage_vs_memory(self):
        result = self.vs.get_summary_data_usage('100',
                                                start_date='2019-3-4',
                                                end_date='2019-4-2',
                                                valid_type='MEMORY_USAGE',
                                                summary_period=300)

        expected = fixtures.SoftLayer_Metric_Tracking_Object.getSummaryData
        self.assertEqual(result, expected)

        args = ('2019-3-4', '2019-4-2', [{"keyName": "MEMORY_USAGE", "summaryType": "max"}], 300)

        self.assert_called_with('SoftLayer_Metric_Tracking_Object', 'getSummaryData', args=args, identifier=1000)

    def test_get_tracking_id(self):
        result = self.vs.get_tracking_id(1234)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'getMetricTrackingObjectId')
        self.assertEqual(result, 1000)

    def test_get_bandwidth_data(self):
        result = self.vs.get_bandwidth_data(1234, '2019-01-01', '2019-02-01', 'public', 1000)
        self.assert_called_with('SoftLayer_Metric_Tracking_Object',
                                'getBandwidthData',
                                args=('2019-01-01', '2019-02-01', 'public', 1000),
                                identifier=1000)
        self.assertEqual(result[0]['type'], 'cpu0')

    def test_get_bandwidth_allocation(self):
        result = self.vs.get_bandwidth_allocation(1234)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'getBandwidthAllotmentDetail', identifier=1234)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'getBillingCycleBandwidthUsage', identifier=1234)
        self.assertEqual(result['allotment']['amount'], '250')
        self.assertEqual(result['usage'][0]['amountIn'], '.448')

    def test_get_bandwidth_allocation_no_allotment(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getBandwidthAllotmentDetail')
        mock.return_value = None

        result = self.vs.get_bandwidth_allocation(1234)

        self.assertEqual(None, result['allotment'])

    def test_get_bandwidth_allocation_with_allotment(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getBandwidthAllotmentDetail')
        mock.return_value = {
            "allocationId": 11111,
            "id": 22222,
            "allocation": {
                "amount": "2000"
            }
        }

        result = self.vs.get_bandwidth_allocation(1234)

        self.assertEqual(2000, int(result['allotment']['amount']))

    def test_get_storage_iscsi_details(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getAttachedNetworkStorages')
        mock.return_value = [
            {
                "accountId": 11111,
                "capacityGb": 12000,
                "id": 3777123,
                "nasType": "ISCSI",
                "username": "SL02SEL31111-9",
            }
        ]

        result = self.vs.get_storage_details(1234, 'ISCSI')

        self.assertEqual([{
            "accountId": 11111,
            "capacityGb": 12000,
            "id": 3777123,
            "nasType": "ISCSI",
            "username": "SL02SEL31111-9",
        }], result)

    def test_get_storage_iscsi_empty_details(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getAttachedNetworkStorages')
        mock.return_value = []

        result = self.vs.get_storage_details(1234, 'ISCSI')

        self.assertEqual([], result)

    def test_get_storage_nas_details(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getAttachedNetworkStorages')
        mock.return_value = [
            {
                "accountId": 11111,
                "capacityGb": 12000,
                "id": 3777111,
                "nasType": "NAS",
                "username": "SL02SEL32222-9",
            }
        ]

        result = self.vs.get_storage_details(1234, 'NAS')

        self.assertEqual([{
            "accountId": 11111,
            "capacityGb": 12000,
            "id": 3777111,
            "nasType": "NAS",
            "username": "SL02SEL32222-9",
        }], result)

    def test_get_storage_nas_empty_details(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getAttachedNetworkStorages')
        mock.return_value = []

        result = self.vs.get_storage_details(1234, 'NAS')

        self.assertEqual([], result)

    def test_get_storage_credentials(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getAllowedHost')
        mock.return_value = {
            "accountId": 11111,
            "id": 33333,
            "name": "iqn.2020-03.com.ibm:sl02su11111-v62941551",
            "resourceTableName": "VIRTUAL_GUEST",
            "credential": {
                "accountId": "11111",
                "id": 44444,
                "password": "SjFDCpHrjskfj",
                "username": "SL02SU11111-V62941551"
            }
        }

        result = self.vs.get_storage_credentials(1234)

        self.assertEqual({
            "accountId": 11111,
            "id": 33333,
            "name": "iqn.2020-03.com.ibm:sl02su11111-v62941551",
            "resourceTableName": "VIRTUAL_GUEST",
            "credential": {
                "accountId": "11111",
                "id": 44444,
                "password": "SjFDCpHrjskfj",
                "username": "SL02SU11111-V62941551"
            }
        }, result)

    def test_get_none_storage_credentials(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getAllowedHost')
        mock.return_value = None

        result = self.vs.get_storage_credentials(1234)

        self.assertEqual(None, result)

    def test_get_portable_storage(self):
        result = self.vs.get_portable_storage(1234)
        self.assert_called_with('SoftLayer_Account',
                                'getPortableStorageVolumes')

        self.assertEqual([
            {
                "capacity": 200,
                "createDate": "2018-10-06T04:27:59-06:00",
                "description": "Disk 2",
                "id": 11111,
                "modifyDate": "",
                "name": "Disk 2",
                "parentId": "",
                "storageRepositoryId": 22222,
                "typeId": 241,
                "units": "GB",
                "uuid": "fd477feb-bf32-408e-882f-02540gghgh111"
            }
        ], result)

    def test_get_portable_storage_empty(self):
        mock = self.set_mock('SoftLayer_Account', 'getPortableStorageVolumes')
        mock.return_value = []

        result = self.vs.get_portable_storage(1234)

        self.assertEqual([], result)

    def test_get_local_disks_system(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getBlockDevices')
        mock.return_value = [
            {
                "createDate": "2018-10-06T04:27:35-06:00",
                "device": "0",
                "id": 11111,
                "mountType": "Disk",
                "diskImage": {
                    "capacity": 100,
                    "description": "adns.vmware.com",
                    "id": 72222,
                    "name": "adns.vmware.com",
                    "units": "GB",
                }
            }
        ]

        result = self.vs.get_local_disks(1234)

        self.assertEqual([
            {
                "createDate": "2018-10-06T04:27:35-06:00",
                "device": "0",
                "id": 11111,
                "mountType": "Disk",
                "diskImage": {
                    "capacity": 100,
                    "description": "adns.vmware.com",
                    "id": 72222,
                    "name": "adns.vmware.com",
                    "units": "GB",
                }
            }
        ], result)

    def test_get_local_disks_empty(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getBlockDevices')
        mock.return_value = []

        result = self.vs.get_local_disks(1234)

        self.assertEqual([], result)

    def test_get_local_disks_swap(self):
        mock = self.set_mock('SoftLayer_Virtual_Guest', 'getBlockDevices')
        mock.return_value = [
            {
                "device": "1",
                "id": 22222,
                "mountType": "Disk",
                "statusId": 1,
                "diskImage": {
                    "capacity": 2,
                    "description": "6211111-SWAP",
                    "id": 33333,
                    "name": "6211111-SWAP",
                    "units": "GB",
                }
            }
        ]

        result = self.vs.get_local_disks(1234)

        self.assertEqual([
            {
                "device": "1",
                "id": 22222,
                "mountType": "Disk",
                "statusId": 1,
                "diskImage": {
                    "capacity": 2,
                    "description": "6211111-SWAP",
                    "id": 33333,
                    "name": "6211111-SWAP",
                    "units": "GB",
                }
            }
        ], result)

    def test_migrate(self):
        result = self.vs.migrate(1234)
        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'migrate', identifier=1234)

    def test_migrate_dedicated(self):
        result = self.vs.migrate_dedicated(1234, 5555)
        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Virtual_Guest', 'migrateDedicatedHost', args=(5555,), identifier=1234)

    def test_get_hardware_guests(self):
        mock = self.set_mock('SoftLayer_Account', 'getHardware')
        mock.return_value = [{
            "accountId": 11111,
            "domain": "vmware.chechu.com",
            "hostname": "host14",
            "id": 22222,
            "virtualHost": {
                "accountId": 11111,
                "id": 33333,
                "name": "host14.vmware.chechu.com",
                "guests": [
                    {
                        "accountId": 11111,
                        "hostname": "NSX-T Manager",
                        "id": 44444,
                        "maxCpu": 16,
                        "maxCpuUnits": "CORE",
                        "maxMemory": 49152,
                        "powerState": {
                            "keyName": "RUNNING",
                            "name": "Running"
                        },
                        "status": {
                            "keyName": "ACTIVE",
                            "name": "Active"
                        }
                    }]}}]

        result = self.vs.get_hardware_guests()
        self.assertEqual("NSX-T Manager", result[0]['virtualHost']['guests'][0]['hostname'])

    def test_authorize_storage(self):
        options = self.vs.authorize_storage(1234, "SL01SEL301234-11")

        self.assertEqual(True, options)

    def test_authorize_storage_empty(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkStorage')
        mock.return_value = []
        self.assertRaises(SoftLayer.exceptions.SoftLayerError,
                          self.vs.authorize_storage,
                          1234, "#")

    def test_authorize_portable_storage(self):
        options = self.vs.attach_portable_storage(1234, 1234567)
        self.assertEqual(1234567, options['id'])
