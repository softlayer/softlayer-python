"""
    SoftLayer.tests.managers.network_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock
import sys
import unittest

import SoftLayer
from SoftLayer import fixtures
from SoftLayer.managers import network
from SoftLayer import testing


class NetworkTests(testing.TestCase):

    def set_up(self):
        self.network = SoftLayer.NetworkManager(self.client)

    def test_ip_lookup(self):
        result = self.network.ip_lookup('10.0.1.37')

        expected = fixtures.SoftLayer_Network_Subnet_IpAddress.getByIpAddress
        self.assertEqual(result, expected)
        self.assert_called_with('SoftLayer_Network_Subnet_IpAddress',
                                'getByIpAddress',
                                args=('10.0.1.37',))

    def test_add_global_ip(self):
        # Test a global IPv4 order
        result = self.network.add_global_ip(test_order=True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

    def test_add_securitygroup_rule(self):
        result = self.network.add_securitygroup_rule(100,
                                                     remote_ip='10.0.0.0/24',
                                                     direction='ingress',
                                                     ethertype='IPv4',
                                                     port_min=95,
                                                     port_max=100,
                                                     protocol='tcp')

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'addRules', identifier=100,
                                args=([{'remoteIp': '10.0.0.0/24',
                                        'direction': 'ingress',
                                        'ethertype': 'IPv4',
                                        'portRangeMin': 95,
                                        'portRangeMax': 100,
                                        'protocol': 'tcp'}],))

    def test_add_securitygroup_rules(self):
        rule1 = {'remoteIp': '10.0.0.0/24',
                 'direction': 'ingress',
                 'ethertype': 'IPv4',
                 'portRangeMin': 95,
                 'portRangeMax': 100,
                 'protocol': 'tcp'}
        rule2 = {'remoteGroupId': 102,
                 'direction': 'egress',
                 'ethertype': 'IPv4'}

        result = self.network.add_securitygroup_rules(100, [rule1, rule2])

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'addRules', identifier=100,
                                args=([rule1, rule2],))

    def test_add_securitygroup_rules_with_dict_error(self):
        rule = {'remoteIp': '10.0.0.0/24',
                'direction': 'ingress'}
        self.assertRaises(TypeError, self.network.add_securitygroup_rules,
                          rule)

    def test_add_subnet_for_ipv4(self):
        # Test a four public address IPv4 order
        result = self.network.add_subnet('public',
                                         quantity=4,
                                         endpoint_id=1234,
                                         version=4,
                                         test_order=True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

        result = self.network.add_subnet('public',
                                         quantity=4,
                                         endpoint_id=1234,
                                         version=4,
                                         test_order=False)

        self.assertEqual(fixtures.SoftLayer_Product_Order.placeOrder, result)

        result = self.network.add_subnet('global',
                                         test_order=True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

    def test_add_subnet_for_ipv6(self):
        # Test a public IPv6 order
        result = self.network.add_subnet('public',
                                         quantity=64,
                                         endpoint_id=45678,
                                         version=6,
                                         test_order=True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

        # Test a global IPv6 order
        result = self.network.add_subnet('global',
                                         version=6,
                                         test_order=True)

        self.assertEqual(fixtures.SoftLayer_Product_Order.verifyOrder, result)

    def test_assign_global_ip(self):
        result = self.network.assign_global_ip(9876, '172.16.24.76')

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Network_Subnet_IpAddress_Global',
                                'route',
                                identifier=9876,
                                args=('172.16.24.76',))

    def test_attach_securitygroup_component(self):
        result = self.network.attach_securitygroup_component(100, 500)

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'attachNetworkComponents',
                                identifier=100,
                                args=([500],))

    def test_attach_securitygroup_components(self):
        result = self.network.attach_securitygroup_components(100, [500, 600])

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'attachNetworkComponents',
                                identifier=100,
                                args=([500, 600],))

    def test_cancel_global_ip(self):
        result = self.network.cancel_global_ip(1234)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelService',
                                identifier=1234)

    def test_cancel_subnet(self):
        result = self.network.cancel_subnet(1234)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelService',
                                identifier=1056)

    def test_create_securitygroup(self):
        result = self.network.create_securitygroup(name='foo',
                                                   description='bar')

        sg_fixture = fixtures.SoftLayer_Network_SecurityGroup
        self.assertEqual(sg_fixture.createObject, result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'createObject',
                                args=({'name': 'foo',
                                       'description': 'bar'},))

    def test_delete_securitygroup(self):
        result = self.network.delete_securitygroup(100)

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'deleteObject',
                                identifier=100)

    def test_detach_securitygroup_component(self):
        result = self.network.detach_securitygroup_component(100, 500)

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'detachNetworkComponents',
                                identifier=100, args=([500],))

    def test_detach_securitygroup_components(self):
        result = self.network.detach_securitygroup_components(100,
                                                              [500, 600])

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'detachNetworkComponents',
                                identifier=100, args=([500, 600],))

    def test_edit_rwhois(self):
        result = self.network.edit_rwhois(
            abuse_email='abuse@test.foo',
            address1='123 Test Street',
            address2='Apt. #31',
            city='Anywhere',
            company_name='TestLayer',
            country='US',
            first_name='Bob',
            last_name='Bobinson',
            postal_code='9ba62',
            private_residence=False,
            state='TX')

        self.assertEqual(result, True)
        expected = {
            'abuseEmail': 'abuse@test.foo',
            'address1': '123 Test Street',
            'address2': 'Apt. #31',
            'city': 'Anywhere',
            'companyName': 'TestLayer',
            'country': 'US',
            'firstName': 'Bob',
            'lastName': 'Bobinson',
            'postalCode': '9ba62',
            'privateResidenceFlag': False,
            'state': 'TX',
        }
        self.assert_called_with('SoftLayer_Network_Subnet_Rwhois_Data',
                                'editObject',
                                identifier='id',
                                args=(expected,))

    def test_edit_securitygroup(self):
        result = self.network.edit_securitygroup(100, name='foobar')

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'editObject', identifier=100,
                                args=({'name': 'foobar'},))

    def test_edit_securitygroup_rule(self):
        result = self.network.edit_securitygroup_rule(100, 500,
                                                      direction='ingress')

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'editRules', identifier=100,
                                args=([{'id': 500,
                                        'direction': 'ingress'}],))

    def test_edit_securitygroup_rule_unset(self):
        # Test calling edit rule with falsy values, which are used
        # to unset those values in the API
        result = self.network.edit_securitygroup_rule(100, 500,
                                                      protocol='',
                                                      port_min=-1,
                                                      port_max=-1,
                                                      ethertype='',
                                                      remote_ip='')

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'editRules', identifier=100,
                                args=([{'id': 500, 'protocol': '',
                                        'portRangeMin': -1, 'portRangeMax': -1,
                                        'ethertype': '', 'remoteIp': ''}],))

    def test_get_rwhois(self):
        result = self.network.get_rwhois()

        self.assertEqual(result, fixtures.SoftLayer_Account.getRwhoisData)
        self.assert_called_with('SoftLayer_Account', 'getRwhoisData')

    def test_get_securitygroup(self):
        result = self.network.get_securitygroup(100)

        sg_fixture = fixtures.SoftLayer_Network_SecurityGroup
        self.assertEqual(sg_fixture.getObject, result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'getObject', identifier=100)

    def test_get_subnet(self):
        result = self.network.get_subnet(9876)

        self.assertEqual(result, fixtures.SoftLayer_Network_Subnet.getObject)
        self.assert_called_with('SoftLayer_Network_Subnet', 'getObject',
                                identifier=9876)

    def test_get_vlan(self):
        result = self.network.get_vlan(1234)

        self.assertEqual(result, fixtures.SoftLayer_Network_Vlan.getObject)
        self.assert_called_with('SoftLayer_Network_Vlan', 'getObject',
                                identifier=1234)

    def test_list_global_ips_default(self):
        result = self.network.list_global_ips()

        self.assertEqual(result,
                         fixtures.SoftLayer_Account.getGlobalIpRecords)
        mask = 'mask[destinationIpAddress[hardware, virtualGuest],ipAddress]'
        self.assert_called_with('SoftLayer_Account', 'getGlobalIpRecords',
                                mask=mask)

    def test_list_global_ips_with_filter(self):
        result = self.network.list_global_ips(version=4)

        self.assertEqual(result,
                         fixtures.SoftLayer_Account.getGlobalIpRecords)
        mask = 'mask[destinationIpAddress[hardware, virtualGuest],ipAddress]'
        _filter = {
            'globalIpRecords': {
                'ipAddress': {
                    'subnet': {
                        'version': {'operation': 4},
                    }
                }
            }
        }
        mask = 'mask[destinationIpAddress[hardware, virtualGuest],ipAddress]'
        self.assert_called_with('SoftLayer_Account', 'getGlobalIpRecords',
                                mask=mask,
                                filter=_filter)

    def test_list_subnets_default(self):
        result = self.network.list_subnets()

        self.assertEqual(result, fixtures.SoftLayer_Account.getSubnets)
        _filter = {'subnets': {'subnetType': {'operation': '!= GLOBAL_IP'}}}
        self.assert_called_with('SoftLayer_Account', 'getSubnets',
                                mask='mask[%s]' % network.DEFAULT_SUBNET_MASK,
                                filter=_filter)

    def test_list_subnets_with_filters(self):
        result = self.network.list_subnets(
            identifier='10.0.0.1',
            datacenter='dal00',
            version=4,
            subnet_type='PRIMARY',
            network_space='PUBLIC',
        )

        self.assertEqual(result, fixtures.SoftLayer_Account.getSubnets)
        _filter = {
            'subnets': {
                'networkIdentifier': {'operation': '_= 10.0.0.1'},
                'datacenter': {
                    'name': {'operation': '_= dal00'}
                },
                'version': {'operation': 4},
                'subnetType': {'operation': '_= PRIMARY'},
                'networkVlan': {'networkSpace': {'operation': '_= PUBLIC'}},
            }
        }

        self.assert_called_with('SoftLayer_Account', 'getSubnets',
                                mask='mask[%s]' % network.DEFAULT_SUBNET_MASK,
                                filter=_filter)

    def test_list_vlans_default(self):
        result = self.network.list_vlans()

        self.assertEqual(result, fixtures.SoftLayer_Account.getNetworkVlans)
        self.assert_called_with('SoftLayer_Account', 'getNetworkVlans')

    def test_list_vlans_with_filters(self):
        result = self.network.list_vlans(
            vlan_number=5,
            datacenter='dal00',
            name='primary-vlan',
        )

        self.assertEqual(result, fixtures.SoftLayer_Account.getNetworkVlans)
        _filter = {
            'networkVlans': {
                'primaryRouter': {
                    'datacenter': {
                        'name': {'operation': '_= dal00'}},
                },
                'vlanNumber': {'operation': 5},
                'name': {'operation': '_= primary-vlan'},
            },
        }
        self.assert_called_with('SoftLayer_Account', 'getNetworkVlans',
                                filter=_filter)

    def test_list_securitygroups(self):
        result = self.network.list_securitygroups()

        sg_fixture = fixtures.SoftLayer_Network_SecurityGroup
        self.assertEqual(sg_fixture.getAllObjects, result)

    def test_list_securitygroup_rules(self):
        result = self.network.list_securitygroup_rules(100)

        sg_fixture = fixtures.SoftLayer_Network_SecurityGroup
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'getRules', identifier=100)
        self.assertEqual(sg_fixture.getRules, result)

    def test_remove_securitygroup_rule(self):
        result = self.network.remove_securitygroup_rule(100, 500)

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'removeRules', identifier=100,
                                args=([500],))

    def test_remove_securitygroup_rules(self):
        result = self.network.remove_securitygroup_rules(100, [500, 600])

        self.assertTrue(result)
        self.assert_called_with('SoftLayer_Network_SecurityGroup',
                                'removeRules', identifier=100,
                                args=([500, 600],))

    def test_summary_by_datacenter(self):
        result = self.network.summary_by_datacenter()

        expected = {'dal00': {'hardware_count': 1,
                              'virtual_guest_count': 1,
                              'subnet_count': 0,
                              'public_ip_count': 6,
                              'vlan_count': 3}}
        self.assertEqual(expected, result)

    def test_resolve_global_ip_ids(self):
        _id = self.network.resolve_global_ip_ids('10.0.0.1')
        self.assertEqual(_id, ['200', '201'])

    def test_resolve_global_ip_ids_no_results(self):
        mock = self.set_mock('SoftLayer_Account', 'getGlobalIpRecords')
        mock.return_value = []

        _id = self.network.resolve_global_ip_ids('nope')

        self.assertEqual(_id, [])

    def test_resolve_subnet_ids(self):
        _id = self.network.resolve_subnet_ids('10.0.0.1/29')
        self.assertEqual(_id, ['100', '111'])

    def test_resolve_subnet_ids_no_results(self):
        mock = self.set_mock('SoftLayer_Account', 'getSubnets')
        mock.return_value = []

        _id = self.network.resolve_subnet_ids('nope')

        self.assertEqual(_id, [])

    def test_resolve_vlan_ids(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkVlans')
        mock.return_value = [{'id': '100'}]

        _id = self.network.resolve_vlan_ids('vlan_name')
        self.assertEqual(_id, ['100'])

    def test_resolve_vlan_ids_no_results(self):
        mock = self.set_mock('SoftLayer_Account', 'getNetworkVlans')
        mock.return_value = []

        _id = self.network.resolve_vlan_ids('nope')

        self.assertEqual(_id, [])

    def test_unassign_global_ip(self):
        result = self.network.unassign_global_ip(9876)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Network_Subnet_IpAddress_Global',
                                'unroute',
                                identifier=9876)

    def test_get_event_logs_by_request_id(self):
        expected = [
            {
                'accountId': 100,
                'eventCreateDate': '2017-10-18T09:40:32.238869-05:00',
                'eventName': 'Security Group Added',
                'ipAddress': '192.168.0.1',
                'label': 'test.softlayer.com',
                'metaData': '{"securityGroupId":"200",'
                            '"securityGroupName":"test_SG",'
                            '"networkComponentId":"100",'
                            '"networkInterfaceType":"public",'
                            '"requestId":"96c9b47b9e102d2e1d81fba"}',
                'objectId': 300,
                'objectName': 'CCI',
                'traceId': '59e767e03a57e',
                'userId': 400,
                'userType': 'CUSTOMER',
                'username': 'user'
            },
            {
                'accountId': 100,
                'eventCreateDate': '2017-10-18T10:42:13.089536-05:00',
                'eventName': 'Security Group Rule(s) Removed',
                'ipAddress': '192.168.0.1',
                'label': 'test_SG',
                'metaData': '{"requestId":"96c9b47b9e102d2e1d81fba",'
                            '"rules":[{"ruleId":"800",'
                            '"remoteIp":null,"remoteGroupId":null,"direction":"ingress",'
                            '"ethertype":"IPv4",'
                            '"portRangeMin":2000,"portRangeMax":2001,"protocol":"tcp"}]}',
                'objectId': 700,
                'objectName': 'Security Group',
                'traceId': '59e7765515e28',
                'userId': 400,
                'userType': 'CUSTOMER',
                'username': 'user'
            }
        ]

        with mock.patch.object(self.network, '_get_cci_event_logs') as cci_mock:
            with mock.patch.object(self.network, '_get_security_group_event_logs') as sg_mock:
                cci_mock.return_value = [
                    {
                        'accountId': 100,
                        'eventCreateDate': '2017-10-18T09:40:32.238869-05:00',
                        'eventName': 'Security Group Added',
                        'ipAddress': '192.168.0.1',
                        'label': 'test.softlayer.com',
                        'metaData': '{"securityGroupId":"200",'
                                    '"securityGroupName":"test_SG",'
                                    '"networkComponentId":"100",'
                                    '"networkInterfaceType":"public",'
                                    '"requestId":"96c9b47b9e102d2e1d81fba"}',
                        'objectId': 300,
                        'objectName': 'CCI',
                        'traceId': '59e767e03a57e',
                        'userId': 400,
                        'userType': 'CUSTOMER',
                        'username': 'user'
                    },
                    {
                        'accountId': 100,
                        'eventCreateDate': '2017-10-23T14:22:36.221541-05:00',
                        'eventName': 'Disable Port',
                        'ipAddress': '192.168.0.1',
                        'label': 'test.softlayer.com',
                        'metaData': '',
                        'objectId': 300,
                        'objectName': 'CCI',
                        'traceId': '100',
                        'userId': '',
                        'userType': 'SYSTEM'
                    },
                    {
                        'accountId': 100,
                        'eventCreateDate': '2017-10-18T09:40:41.830338-05:00',
                        'eventName': 'Security Group Rule Added',
                        'ipAddress': '192.168.0.1',
                        'label': 'test.softlayer.com',
                        'metaData': '{"securityGroupId":"200",'
                                    '"securityGroupName":"test_SG",'
                                    '"networkComponentId":"100",'
                                    '"networkInterfaceType":"public",'
                                    '"requestId":"53d0b91d392864e062f4958",'
                                    '"rules":[{"ruleId":"100",'
                                    '"remoteIp":null,"remoteGroupId":null,"direction":"ingress",'
                                    '"ethertype":"IPv4",'
                                    '"portRangeMin":2000,"portRangeMax":2001,"protocol":"tcp"}]}',
                        'objectId': 300,
                        'objectName': 'CCI',
                        'traceId': '59e767e9c2184',
                        'userId': 400,
                        'userType': 'CUSTOMER',
                        'username': 'user'
                    }
                ]

                sg_mock.return_value = [
                    {
                        'accountId': 100,
                        'eventCreateDate': '2017-10-18T10:42:13.089536-05:00',
                        'eventName': 'Security Group Rule(s) Removed',
                        'ipAddress': '192.168.0.1',
                        'label': 'test_SG',
                        'metaData': '{"requestId":"96c9b47b9e102d2e1d81fba",'
                                    '"rules":[{"ruleId":"800",'
                                    '"remoteIp":null,"remoteGroupId":null,"direction":"ingress",'
                                    '"ethertype":"IPv4",'
                                    '"portRangeMin":2000,"portRangeMax":2001,"protocol":"tcp"}]}',
                        'objectId': 700,
                        'objectName': 'Security Group',
                        'traceId': '59e7765515e28',
                        'userId': 400,
                        'userType': 'CUSTOMER',
                        'username': 'user'
                    },
                    {
                        'accountId': 100,
                        'eventCreateDate': '2017-10-18T10:42:11.679736-05:00',
                        'eventName': 'Network Component Removed from Security Group',
                        'ipAddress': '192.168.0.1',
                        'label': 'test_SG',
                        'metaData': '{"requestId":"6b9a87a9ab8ac9a22e87a00",'
                                    '"fullyQualifiedDomainName":"test.softlayer.com",'
                                    '"networkComponentId":"100",'
                                    '"networkInterfaceType":"public"}',
                        'objectId': 700,
                        'objectName': 'Security Group',
                        'traceId': '59e77653a1e5f',
                        'userId': 400,
                        'userType': 'CUSTOMER',
                        'username': 'user'
                    }
                ]

                result = self.network.get_event_logs_by_request_id('96c9b47b9e102d2e1d81fba')

        self.assertEqual(expected, result)

    @unittest.skipIf(sys.version_info < (3, 6), "__next__ doesn't work in python 2")
    def test_get_security_group_event_logs(self):
        result = self.network._get_security_group_event_logs()
        # Event log now returns a generator, so you have to get a result for it to make an API call
        log = result.__next__()
        _filter = {'objectName': {'operation': 'Security Group'}}
        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects', filter=_filter)
        self.assertEqual(100, log['accountId'])

    @unittest.skipIf(sys.version_info < (3, 6), "__next__ doesn't work in python 2")
    def test_get_cci_event_logs(self):
        result = self.network._get_cci_event_logs()
        # Event log now returns a generator, so you have to get a result for it to make an API call
        log = result.__next__()
        _filter = {'objectName': {'operation': 'CCI'}}
        self.assert_called_with('SoftLayer_Event_Log', 'getAllObjects', filter=_filter)
        self.assertEqual(100, log['accountId'])
