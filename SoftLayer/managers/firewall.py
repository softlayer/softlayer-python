"""
    SoftLayer.firewall
    ~~~~~~~~~~~~~~~~~~
    Firewall Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""


def has_firewall(vlan):
    return bool(
        vlan.get('dedicatedFirewallFlag', None) or
        vlan.get('highAvailabilityFirewallFlag', None) or
        vlan.get('firewallInterfaces', None) or
        vlan.get('firewallNetworkComponents', None) or
        vlan.get('firewallGuestNetworkComponents', None)
    )


class FirewallManager(object):
    def __init__(self, client):
        """ Manages firewalls.

        :param SoftLayer.API.Client client: the API client instance

        """
        self.client = client

    def get_firewalls(self):
        results = self.client['Account'].getObject(
            mask={
                'networkVlans': {
                    'firewallNetworkComponents': None,
                    'networkVlanFirewall': None,
                    'dedicatedFirewallFlag': None,
                    'firewallGuestNetworkComponents': None,
                    'firewallInterfaces': {},
                    'firewallRules': None,
                    'highAvailabilityFirewallFlag': None,
                    #'primarySubnet': None,
                }
            })['networkVlans']

        return filter(has_firewall, results)
