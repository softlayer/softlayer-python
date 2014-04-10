"""
    SoftLayer.firewall
    ~~~~~~~~~~~~~~~~~~
    Firewall Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.utils import IdentifierMixin, NestedDict, query_filter

RULE_MASK = ('mask[orderValue,action,destinationIpAddress,'
             'destinationIpSubnetMask,protocol,destinationPortRangeStart,'
             'destinationPortRangeEnd,sourceIpAddress,sourceIpSubnetMask,'
             'version]')


def has_firewall(vlan):
    """ Helper to determine whether or not a VLAN has a firewall.

    :param dict vlan: A dictionary representing a VLAN
    :returns: True if the VLAN has a firewall, false if it doesn't.
    """
    return bool(
        vlan.get('dedicatedFirewallFlag', None) or
        vlan.get('highAvailabilityFirewallFlag', None) or
        vlan.get('firewallInterfaces', None) or
        vlan.get('firewallNetworkComponents', None) or
        vlan.get('firewallGuestNetworkComponents', None)
    )


class FirewallManager(IdentifierMixin, object):

    """ Manages firewalls.

    :param SoftLayer.API.Client client: the API client instance

    """

    def __init__(self, client):
        self.client = client
        self.account = self.client['Account']
        self.prod_pkg = self.client['Product_Package']

    def get_std_fwl_pkg(self, server_id, is_cci=True):
        """ Retrieves the standard firewall package for the CCI.

        :param int server_id: The ID of the server to create the firewall for
        :param bool is_cci: True if the id provided is for a CCI,
                            False for a server
        :returns: A dictionary containing the standard CCI firewall package
        """
        mask = ('mask[primaryNetworkComponent[speed]]')
        if is_cci:
            svc = self.client['Virtual_Guest']
        else:
            svc = self.client['Hardware_Server']

        item = svc.getObject(mask=mask, id=server_id)

        _filter = NestedDict({})
        _value = "%s%s" % (item['primaryNetworkComponent']['speed'],
                           "Mbps Hardware Firewall")
        _filter['items']['description'] = query_filter(_value)

        kwargs = NestedDict({})
        kwargs['id'] = 0  # look at package id 0
        kwargs['filter'] = _filter.to_dict()
        return self.prod_pkg.getItems(**kwargs)

    def get_dedicated_fwl_pkg(self, ha_enabled=False):
        """ Retrieves the dedicated firewall package.

        :param bool ha_enabled: True if HA is to be enabled on the firewall
                                False for No HA
        :returns: A dictionary containing the dedicated CCI firewall package
        """

        fwl_filter = 'Hardware Firewall (Dedicated)'
        ha_fwl_filter = 'Hardware Firewall (High Availability)'
        _filter = NestedDict({})
        if ha_enabled:
            _filter['items']['description'] = query_filter(ha_fwl_filter)
        else:
            _filter['items']['description'] = query_filter(fwl_filter)

        kwargs = NestedDict({})
        kwargs['id'] = 0  # look at package id 0
        kwargs['filter'] = _filter.to_dict()
        return self.prod_pkg.getItems(**kwargs)

    def cancel_firewall(self, firewall_id, dedicated=False):
        """ Cancels the specified firewall.

        :param int firewall_id: Firewall ID to be cancelled.
        :param bool dedicated: If true, the firewall instance is dedicated,
                               otherwise, the firewall instance is shared.
        """
        fwl_billing = self.get_fwl_billing_item(firewall_id, dedicated)
        billing_id = fwl_billing['billingItem']['id']
        billing_item = self.client['Billing_Item']
        return billing_item.cancelService(id=billing_id)

    def add_standard_firewall(self, server_id, is_cci=True):
        """ Creates a firewall for the specified CCI/Server

        :param int cci_id: The ID of the CCI to create the firewall for
        :param bool is_cci: If false, will create the firewall for a server,
                            otherwise for a CCI
        :returns: A dictionary containing the standard CCI firewall order
        """
        package = self.get_std_fwl_pkg(server_id, is_cci)
        if is_cci:
            product_order = {
                'complexType': 'SoftLayer_Container_Product_Order_Network_'
                               'Protection_Firewall',
                'quantity': 1,
                'packageId': 0,
                'virtualGuests': [{'id': server_id}],
                'prices': [{'id': package[0]['prices'][0]['id']}]
            }
        else:
            product_order = {
                'complexType': 'SoftLayer_Container_Product_Order_Network_'
                               'Protection_Firewall',
                'quantity': 1,
                'packageId': 0,
                'hardware': [{'id': server_id}],
                'prices': [{'id': package[0]['prices'][0]['id']}]
            }
        return self.client['Product_Order'].placeOrder(product_order)

    def add_vlan_firewall(self, vlan_id, ha_enabled=False):
        """ Creates a firewall for the specified vlan

        :param int vlan_id: The ID of the vlan to create the firewall for
        :param bool ha_enabled: If True, Ha firewall will be created

        :returns: A dictionary containing the VLAN firewall order
        """
        package = self.get_dedicated_fwl_pkg(ha_enabled)
        product_order = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_'
                           'Protection_Firewall_Dedicated',
            'quantity': 1,
            'packageId': 0,
            'vlanId': vlan_id,
            'prices': [{'id': package[0]['prices'][0]['id']}]
        }
        return self.client['Product_Order'].placeOrder(product_order)

    def get_fwl_billing_item(self, firewall_id, dedicated=False):
        """ Retrieves the billing item of the firewall

        :param int firewall_id: Firewall ID to get the billing item for
        :param bool dedicated: whether the firewall is dedicated or standard
        :returns: A dictionary of the firewall billing item.
        """
        mask = ('mask[id,billingItem[id]]')
        if dedicated:
            fwl_svc = self.client['Network_Vlan_Firewall']
        else:
            fwl_svc = self.client['Network_Component_Firewall']
        return fwl_svc.getObject(id=firewall_id, mask=mask)

    def get_firewalls(self):
        """ Returns a list of all firewalls on the account.

        :returns: A list of firewalls on the current account.
        """
        results = self.account.getObject(
            mask={
                'networkVlans': {
                    'firewallNetworkComponents': None,
                    'networkVlanFirewall': None,
                    'dedicatedFirewallFlag': None,
                    'firewallGuestNetworkComponents': None,
                    'firewallInterfaces': {},
                    'firewallRules': None,
                    'highAvailabilityFirewallFlag': None,
                    # 'primarySubnet': None,
                }
            })['networkVlans']
        return [firewall for firewall in results
                if has_firewall(firewall)]

    def get_standard_fwl_rules(self, firewall_id):
        """ Get the rules of a standard firewall

        :param integer firewall_id: the instance ID of the standard firewall
        :returns: A list of the rules.
        """
        svc = self.client['Network_Component_Firewall']
        return svc.getRules(id=firewall_id, mask=RULE_MASK)

    def get_dedicated_fwl_rules(self, firewall_id):
        """ Get the rules of a dedicated firewall

        :param integer firewall_id: the instance ID of the dedicated firewall
        :returns: A list of the rules.
        """
        svc = self.client['Network_Vlan_Firewall']
        return svc.getRules(id=firewall_id, mask=RULE_MASK)

    def edit_dedicated_fwl_rules(self, firewall_id, rules):
        """ Edit the rules for dedicated firewall

        :param integer firewall_id: the instance ID of the dedicated firewall
        :param dict rules: the rules to be pushed on the firewall
        """
        mask = ('mask[networkVlan[firewallInterfaces'
                '[firewallContextAccessControlLists]]]')
        svc = self.client['Network_Vlan_Firewall']
        fwl = svc.getObject(id=firewall_id, mask=mask)
        network_vlan = fwl['networkVlan']

        for fwl1 in network_vlan['firewallInterfaces']:
            if fwl1['name'] == 'inside':
                continue
            for control_list in fwl1['firewallContextAccessControlLists']:
                if control_list['direction'] == 'out':
                    continue
                fwl_ctx_acl_id = control_list['id']

        template = {
            'firewallContextAccessControlListId': fwl_ctx_acl_id,
            'rules': rules
        }

        svc = self.client['Network_Firewall_Update_Request']
        return svc.createObject(template)

    def edit_standard_fwl_rules(self, firewall_id, rules):
        """ Edit the rules for standard firewall

        :param integer firewall_id: the instance ID of the standard firewall
        :param dict rules: the rules to be pushed on the firewall
        """
        rule_svc = self.client['Network_Firewall_Update_Request']
        template = {
            "networkComponentFirewallId": firewall_id,
            "rules": rules}

        return rule_svc.createObject(template)
