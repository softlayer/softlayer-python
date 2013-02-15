
__all__ = ['FirewallManager']


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
        """ Firewall manager

        :param client: SoftLayer.API.Client
        """
        self.client = client

    def get_firewalls(self):
        results = filter(has_firewall, self.client['Account'].getObject(
            mask={'networkVlans': {
                'firewallNetworkComponents': None,
                'networkVlanFirewall': None,
                'dedicatedFirewallFlag': None,
                'firewallGuestNetworkComponents': None,
                'firewallInterfaces': {},
                'firewallRules': None,
                'highAvailabilityFirewallFlag': None,
                #'primarySubnet': None,
            }})['networkVlans'])

        return results
