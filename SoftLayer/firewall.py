
__all__ = ['FirewallManager']


class FirewallManager(object):
    def __init__(self, client):
        """ Firewall manager

        :param client: SoftLayer.API.Client
        """
        self.client = client

    def list(self):
        return self.client['Account'].getObject(
            mask={'networkVlans': {
                'firewallNetworkComponents': None,
                'networkVlanFirewall': None,
                'dedicatedFirewallFlag': None,
                'firewallGuestNetworkComponents': None,
                'firewallInterfaces': {},
                'firewallRules': None,
                'highAvailabilityFirewallFlag': None,
                #'primarySubnet': None,
            }})
