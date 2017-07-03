"""
    SoftLayer.tests.managers.firewall_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer
from SoftLayer import exceptions
from SoftLayer import fixtures
from SoftLayer import testing


class FirewallTests(testing.TestCase):

    def set_up(self):
        self.firewall = SoftLayer.FirewallManager(self.client)

    def test_get_firewalls(self):
        firewall_vlan = {
            'id': 1,
            'firewallNetworkComponents': [{'id': 1234}],
            'networkVlanFirewall': {'id': 1234},
            'dedicatedFirewallFlag': True,
            'firewallGuestNetworkComponents': [{'id': 1234}],
            'firewallInterfaces': [{'id': 1234}],
            'firewallRules': [{'id': 1234}],
            'highAvailabilityFirewallFlag': True,
        }
        mock = self.set_mock('SoftLayer_Account', 'getNetworkVlans')
        mock.return_value = [firewall_vlan]

        firewalls = self.firewall.get_firewalls()

        self.assertEqual(firewalls, [firewall_vlan])
        self.assert_called_with('SoftLayer_Account', 'getNetworkVlans')

    def test_get_standard_fwl_rules(self):
        rules = self.firewall.get_standard_fwl_rules(1234)

        self.assertEqual(
            rules,
            fixtures.SoftLayer_Network_Component_Firewall.getRules)
        self.assert_called_with('SoftLayer_Network_Component_Firewall',
                                'getRules',
                                identifier=1234)

    def test_get_dedicated_fwl_rules(self):

        rules = self.firewall.get_dedicated_fwl_rules(1234)

        self.assertEqual(rules,
                         fixtures.SoftLayer_Network_Vlan_Firewall.getRules)
        self.assert_called_with('SoftLayer_Network_Vlan_Firewall', 'getRules',
                                identifier=1234)

    def test_get_standard_package_virtual_server(self):
        # test standard firewalls
        self.firewall.get_standard_package(server_id=1234, is_virt=True)

        self.assert_called_with('SoftLayer_Virtual_Guest', 'getObject',
                                identifier=1234,
                                mask='mask[primaryNetworkComponent[maxSpeed]]')

        _filter = {
            'items': {
                'description': {
                    'operation': '_= 100Mbps Hardware Firewall'
                }
            }
        }
        self.assert_called_with('SoftLayer_Product_Package', 'getItems',
                                identifier=0,
                                filter=_filter)

    def test_get_standard_package_bare_metal(self):
        self.firewall.get_standard_package(server_id=1234, is_virt=False)

        # we should ask for the frontEndNetworkComponents to get
        # the firewall port speed
        mask = 'mask[id,maxSpeed,networkComponentGroup.networkComponents]'
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'getFrontendNetworkComponents',
                                identifier=1234,
                                mask=mask)

        # shiould call the product package for a 2000Mbps firwall
        _filter = {
            'items': {
                'description': {
                    'operation': '_= 2000Mbps Hardware Firewall'
                }
            }
        }
        self.assert_called_with('SoftLayer_Product_Package', 'getItems',
                                identifier=0,
                                filter=_filter)

    def test_get_dedicated_package_ha(self):
        # test dedicated HA firewalls
        self.firewall.get_dedicated_package(ha_enabled=True)

        _filter = {
            'items': {
                'description': {
                    'operation': '_= Hardware Firewall (High Availability)'
                }
            }
        }
        self.assert_called_with('SoftLayer_Product_Package', 'getItems',
                                identifier=0,
                                filter=_filter)

    def test_get_dedicated_package_pkg(self):
        # test dedicated HA firewalls
        self.firewall.get_dedicated_package(ha_enabled=False)

        _filter = {
            'items': {
                'description': {
                    'operation': '_= Hardware Firewall (Dedicated)'
                }
            }
        }
        self.assert_called_with('SoftLayer_Product_Package', 'getItems',
                                identifier=0,
                                filter=_filter)

    def test_cancel_firewall(self):
        # test standard firewalls
        result = self.firewall.cancel_firewall(6327, dedicated=False)

        self.assertEqual(result, fixtures.SoftLayer_Billing_Item.cancelService)
        self.assert_called_with('SoftLayer_Network_Component_Firewall',
                                'getObject',
                                identifier=6327,
                                mask='mask[id,billingItem[id]]')
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelService',
                                identifier=21370814)

    def test_cancel_firewall_no_firewall(self):
        mock = self.set_mock('SoftLayer_Network_Component_Firewall', 'getObject')
        mock.return_value = None

        self.assertRaises(exceptions.SoftLayerError,
                          self.firewall.cancel_firewall, 6327, dedicated=False)

    def test_cancel_firewall_no_billing(self):
        mock = self.set_mock('SoftLayer_Network_Component_Firewall', 'getObject')
        mock.return_value = {
            'id': 6327,
            'billingItem': None
        }

        self.assertRaises(exceptions.SoftLayerError,
                          self.firewall.cancel_firewall, 6327, dedicated=False)

    def test_cancel_dedicated_firewall(self):
        # test dedicated firewalls
        result = self.firewall.cancel_firewall(6327, dedicated=True)

        self.assertEqual(result, fixtures.SoftLayer_Billing_Item.cancelService)
        self.assert_called_with('SoftLayer_Network_Vlan_Firewall',
                                'getObject',
                                identifier=6327,
                                mask='mask[id,billingItem[id]]')
        self.assert_called_with('SoftLayer_Billing_Item', 'cancelService',
                                identifier=21370815)

    def test_cancel_dedicated_firewall_no_firewall(self):
        mock = self.set_mock('SoftLayer_Network_Vlan_Firewall', 'getObject')
        mock.return_value = None

        self.assertRaises(exceptions.SoftLayerError,
                          self.firewall.cancel_firewall, 6327, dedicated=True)

    def test_cancel_dedicated_firewall_no_billing(self):
        mock = self.set_mock('SoftLayer_Network_Vlan_Firewall', 'getObject')
        mock.return_value = {
            'id': 6327,
            'billingItem': None
        }
        self.assertRaises(exceptions.SoftLayerError,
                          self.firewall.cancel_firewall, 6327, dedicated=True)

    def test_add_standard_firewall_virtual_server(self):
        # test standard firewalls for virtual servers
        self.firewall.add_standard_firewall(6327, is_virt=True)

        self.assert_called_with('SoftLayer_Virtual_Guest', 'getObject',
                                mask='mask[primaryNetworkComponent[maxSpeed]]',
                                identifier=6327)

        _filter = {
            'items': {
                'description': {
                    'operation': '_= 100Mbps Hardware Firewall'
                }
            }
        }
        self.assert_called_with('SoftLayer_Product_Package', 'getItems',
                                filter=_filter,
                                identifier=0)

        args = ({'prices': [{'id': 1122}],
                 'quantity': 1,
                 'virtualGuests': [{'id': 6327}],
                 'packageId': 0,
                 'complexType': 'SoftLayer_Container_Product_Order_Network_'
                                'Protection_Firewall'},)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=args)

    def test_add_standard_firewall_server(self):
        # test dedicated firewall for Servers
        self.firewall.add_standard_firewall(6327, is_virt=False)

        # We should query the product package for a 2000Mbps firewall
        _filter = {
            'items': {
                'description': {
                    'operation': '_= 2000Mbps Hardware Firewall'
                }
            }
        }
        self.assert_called_with('SoftLayer_Product_Package', 'getItems',
                                identifier=0,
                                filter=_filter)

        # we should ask for the frontEndNetworkComponents to get
        # the firewall port speed
        mask = 'mask[id,maxSpeed,networkComponentGroup.networkComponents]'
        self.assert_called_with('SoftLayer_Hardware_Server',
                                'getFrontendNetworkComponents',
                                mask=mask,
                                identifier=6327)

        args = ({'hardware': [{'id': 6327}],
                 'prices': [{'id': 1122}],
                 'quantity': 1,
                 'packageId': 0,
                 'complexType': 'SoftLayer_Container_Product_Order_Network_'
                                'Protection_Firewall'},)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=args)

    def test__get_fwl_port_speed_server(self):
        # Test the routine that calculates the speed of firewall
        # required for a server
        port_speed = self.firewall._get_fwl_port_speed(186908, False)

        self.assertEqual(port_speed, 2000)

    def test_add_vlan_firewall(self):
        # test dedicated firewall for Vlan
        self.firewall.add_vlan_firewall(6327, ha_enabled=False)

        _filter = {
            'items': {
                'description': {
                    'operation': '_= Hardware Firewall (Dedicated)'
                }
            }
        }
        self.assert_called_with('SoftLayer_Product_Package', 'getItems',
                                identifier=0,
                                filter=_filter)

        args = ({'prices': [{'id': 1122}],
                 'quantity': 1,
                 'vlanId': 6327,
                 'packageId': 0,
                 'complexType': 'SoftLayer_Container_Product_Order_Network_'
                                'Protection_Firewall_Dedicated'},)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=args)

    def test_add_vlan_firewall_ha(self):
        # test dedicated firewall for Vlan
        self.firewall.add_vlan_firewall(6327, ha_enabled=True)

        _filter = {
            'items': {
                'description': {
                    'operation': '_= Hardware Firewall (High Availability)'
                }
            }
        }
        self.assert_called_with('SoftLayer_Product_Package', 'getItems',
                                identifier=0,
                                filter=_filter)

        args = ({'prices': [{'id': 1122}],
                 'quantity': 1,
                 'vlanId': 6327,
                 'packageId': 0,
                 'complexType': 'SoftLayer_Container_Product_Order_Network_'
                                'Protection_Firewall_Dedicated'},)
        self.assert_called_with('SoftLayer_Product_Order', 'placeOrder',
                                args=args)

    def test_edit_dedicated_fwl_rules(self):
        # test standard firewalls
        rules = fixtures.SoftLayer_Network_Vlan_Firewall.getRules
        self.firewall.edit_dedicated_fwl_rules(firewall_id=1234,
                                               rules=rules)

        args = ({'firewallContextAccessControlListId': 3142,
                 'rules': rules},)
        self.assert_called_with('SoftLayer_Network_Firewall_Update_Request',
                                'createObject',
                                args=args)

    def test_edit_standard_fwl_rules(self):
        # test standard firewalls
        rules = fixtures.SoftLayer_Network_Component_Firewall.getRules
        self.firewall.edit_standard_fwl_rules(firewall_id=1234,
                                              rules=rules)

        args = ({"networkComponentFirewallId": 1234,
                 "rules": rules},)
        self.assert_called_with('SoftLayer_Network_Firewall_Update_Request',
                                'createObject',
                                args=args)
