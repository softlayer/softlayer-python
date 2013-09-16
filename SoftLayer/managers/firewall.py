"""
    SoftLayer.firewall
    ~~~~~~~~~~~~~~~~~~
    Firewall Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""


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


class FirewallManager(object):
    """ Manages firewalls.

    :param SoftLayer.API.Client client: the API client instance

    """
    def __init__(self, client):
        #: A valid `SoftLayer.API.Client` object that will be used for all
        #: actions.
        self.client = client

    def get_firewalls(self):
        """ Returns a list of all firewalls on the account.

        :returns: A list of firewalls on the current account.
        """
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
