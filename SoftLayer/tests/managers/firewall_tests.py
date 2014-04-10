"""
    SoftLayer.tests.managers.firewall_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import FirewallManager
from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.tests.fixtures import (Account, Network_Component_Firewall,
                                      Network_Vlan_Firewall, Billing_Item)
from mock import ANY


MASK = ('mask[orderValue,action,destinationIpAddress,destinationIpSubnetMask,'
        'protocol,destinationPortRangeStart,destinationPortRangeEnd,'
        'sourceIpAddress,sourceIpSubnetMask,version]')


class FirewallTests(unittest.TestCase):

    def setUp(self):
        self.client = FixtureClient()
        self.firewall = FirewallManager(self.client)

    def test_get_firewalls(self):
        call = self.client['Account'].getObject

        firewalls = self.firewall.get_firewalls()

        call.assert_called_once_with(mask=ANY)
        self.assertEqual(firewalls, Account.getObject['networkVlans'])

    def test_get_standard_fwl_rules(self):
        call = self.client['Network_Component_Firewall'].getRules

        rules = self.firewall.get_standard_fwl_rules(1234)
        call.assert_called_once_with(id=1234, mask=MASK)
        self.assertEqual(rules, Network_Component_Firewall.getRules)

    def test_get_dedicated_fwl_rules(self):
        call = self.client['Network_Vlan_Firewall'].getRules

        rules = self.firewall.get_dedicated_fwl_rules(1234)
        call.assert_called_once_with(id=1234, mask=MASK)
        self.assertEqual(rules, Network_Vlan_Firewall.getRules)

    def test_get_fwl_billing_item(self):

        # test standard firewalls
        call = self.client['Network_Component_Firewall'].getObject
        MASK = ('mask[id,billingItem[id]]')
        item = self.firewall.get_fwl_billing_item(firewall_id=1234,
                                                  dedicated=False)
        call.assert_called_once_with(id=1234, mask=MASK)
        billingItemId = 21370814
        self.assertEqual(item['billingItem']['id'], billingItemId)

        # test dedicated firewalls
        call = self.client['Network_Vlan_Firewall'].getObject
        MASK = ('mask[id,billingItem[id]]')
        item = self.firewall.get_fwl_billing_item(firewall_id=12345,
                                                  dedicated=True)
        call.assert_called_once_with(id=12345, mask=MASK)
        billingItemId = 21370815
        self.assertEqual(item['billingItem']['id'], billingItemId)

    def test_get_std_fwl_pkg(self):
        # test standard firewalls
        self.firewall.get_std_fwl_pkg(server_id=1234, is_cci=True)
        call2 = self.client['Virtual_Guest'].getObject
        mask = ('mask[primaryNetworkComponent[speed]]')
        f = self.client['Product_Package'].getItems
        _filter = {
            'items': {
                'description': {
                    'operation': '_= 10Mbps Hardware Firewall'
                    }
                }
            }
        f.assert_called_once_with(filter=_filter, id=0)
        call2.assert_called_once_with(id=1234, mask=mask)

        self.firewall.get_std_fwl_pkg(server_id=1234, is_cci=False)
        call2 = self.client['Hardware_Server'].getObject
        mask = ('mask[primaryNetworkComponent[speed]]')
        f = self.client['Product_Package'].getItems
        _filter = {
            'items': {
                'description': {
                    'operation': '_= 10Mbps Hardware Firewall'
                    }
                }
            }
        f.assert_called_twice_with(filter=_filter, id=0)
        call2.assert_called_once_with(id=1234, mask=mask)

    def test_get_dedicated_fwl_pkg_ha(self):
        # test dedicated HA firewalls
        self.firewall.get_dedicated_fwl_pkg(ha_enabled=True)
        f = self.client['Product_Package'].getItems
        _filter = {
            'items': {
                'description': {
                    'operation': '_= Hardware Firewall (High Availability)'
                    }
                }
            }
        f.assert_called_once_with(filter=_filter, id=0)

    def test_get_dedicated_fwl_pkg(self):
        # test dedicated HA firewalls
        self.firewall.get_dedicated_fwl_pkg(ha_enabled=False)
        f = self.client['Product_Package'].getItems
        _filter = {
            'items': {
                'description': {
                    'operation': '_= Hardware Firewall (Dedicated)'
                    }
                }
            }
        f.assert_called_once_with(filter=_filter, id=0)

    def test_cancel_firewall(self):
        # test standard firewalls
        fwl_id = 6327
        billing_item_id = 21370814
        result = self.firewall.cancel_firewall(fwl_id, dedicated=False)
        f = self.client['Billing_Item'].cancelService
        f.assert_called_once_with(id=billing_item_id)
        self.assertEqual(result, Billing_Item.cancelService)
        call = self.client['Network_Component_Firewall'].getObject
        MASK = ('mask[id,billingItem[id]]')
        call.assert_called_once_with(id=6327, mask=MASK)
        # test dedicated firewalls
        billing_item_id = 21370815
        result = self.firewall.cancel_firewall(fwl_id, dedicated=True)
        f = self.client['Billing_Item'].cancelService
        f.assert_called_twice_with(id=billing_item_id)
        self.assertEqual(result, Billing_Item.cancelService)
        call = self.client['Network_Vlan_Firewall'].getObject
        MASK = ('mask[id,billingItem[id]]')
        call.assert_called_once_with(id=6327, mask=MASK)

    def test_add_standard_firewall_cci(self):
        # test standard firewalls for CCI
        server_id = 6327
        self.firewall.add_standard_firewall(server_id, is_cci=True)
        f = self.client['Product_Package'].getItems
        _filter = {
            'items': {
                'description': {
                    'operation': '_= 10Mbps Hardware Firewall'
                    }
                }
            }
        f.assert_called_once_with(filter=_filter, id=0)

        call2 = self.client['Virtual_Guest'].getObject
        mask = ('mask[primaryNetworkComponent[speed]]')
        call2.assert_called_once_with(id=6327, mask=mask)
        f = self.client['Product_Order'].placeOrder
        f.assert_called_once()

    def test_add_standard_firewall_server(self):
        # test dedicated firewall for Servers
        server_id = 6327
        mask = ('mask[primaryNetworkComponent[speed]]')
        self.firewall.add_standard_firewall(server_id, is_cci=False)
        f = self.client['Product_Order'].placeOrder
        f.assert_called_once()

        f = self.client['Product_Package'].getItems
        _filter = {
            'items': {
                'description': {
                    'operation': '_= 10Mbps Hardware Firewall'
                    }
                }
            }
        f.assert_called_once_with(filter=_filter, id=0)

        call2 = self.client['Hardware_Server'].getObject
        call2.assert_called_once_with(id=6327, mask=mask)

    def test_add_vlan_firewall(self):
        # test dedicated firewall for Vlan
        vlan_id = 6327
        self.firewall.add_vlan_firewall(vlan_id, ha_enabled=False)
        f = self.client['Product_Order'].placeOrder
        f.assert_called_once()

        f = self.client['Product_Package'].getItems
        _filter = {
            'items': {
                'description': {
                    'operation': '_= Hardware Firewall (Dedicated)'
                    }
                }
            }
        f.assert_called_once_with(filter=_filter, id=0)

    def test_add_vlan_firewall_ha(self):
        # test dedicated firewall for Vlan
        vlan_id = 6327
        self.firewall.add_vlan_firewall(vlan_id, ha_enabled=True)
        f = self.client['Product_Order'].placeOrder
        f.assert_called_once()

        f = self.client['Product_Package'].getItems
        _filter = {
            'items': {
                'description': {
                    'operation': '_= Hardware Firewall (High Availability)'
                    }
                }
            }

        f.assert_called_once_with(filter=_filter, id=0)

    def test_edit_dedicated_fwl_rules(self):
        # test standard firewalls
        rules = Network_Vlan_Firewall.getRules
        fwl_id = 1234
        fwl_ctx_acl_id = 3142
        self.firewall.edit_dedicated_fwl_rules(firewall_id=fwl_id,
                                               rules=rules)
        template = {
            'firewallContextAccessControlListId': fwl_ctx_acl_id,
            'rules': rules
        }
        f = self.client['Network_Firewall_Update_Request'].createObject
        f.assert_called_once_with(template)

    def test_edit_standard_fwl_rules(self):
        # test standard firewalls
        rules = Network_Component_Firewall.getRules
        fwl_id = 1234
        self.firewall.edit_standard_fwl_rules(firewall_id=fwl_id,
                                              rules=rules)
        tempObject = {
            "networkComponentFirewallId": fwl_id,
            "rules": rules}
        f = self.client['Network_Firewall_Update_Request'].createObject

        f.assert_called_once_with(tempObject)
