"""
usage: sl firewall [<command>] [<args>...] [options]

Firewall rule and security management

The available commands are:
  list  List active vlans with firewalls

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from SoftLayer.CLI import CLIRunnable, Table, listing
from SoftLayer.firewall import FirewallManager


class FWList(CLIRunnable):
    """
usage: sl firewall list [options]

List active vlans with firewalls
"""
    action = 'list'

    @staticmethod
    def execute(client, args):
        f = FirewallManager(client)
        fwvlans = f.get_firewalls()
        t = Table(['vlan', 'type', 'features'])

        dedicatedfws = filter(lambda x: x['dedicatedFirewallFlag'], fwvlans)
        for vlan in dedicatedfws:
            features = []
            if vlan['highAvailabilityFirewallFlag']:
                features.append('HA')
            t.add_row([
                vlan['vlanNumber'],
                'dedicated',
                listing(features, separator=','),
            ])

        shared_vlan = filter(lambda x: not x['dedicatedFirewallFlag'], fwvlans)
        for vlan in shared_vlan:
            t.add_row([vlan['vlanNumber'], 'standard', ''])

        return t
