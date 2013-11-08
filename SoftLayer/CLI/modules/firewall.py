"""
usage: sl firewall [<command>] [<args>...] [options]

Firewall rule and security management

The available commands are:
  list  List active vlans with firewalls
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import CLIRunnable, Table, listing
from SoftLayer.CLI.helpers import blank
from SoftLayer import FirewallManager


class FWList(CLIRunnable):
    """
usage: sl firewall list [options]

List active vlans with firewalls
"""
    action = 'list'

    def execute(self, args):
        f = FirewallManager(self.client)
        fwvlans = f.get_firewalls()
        t = Table(['vlan', 'type', 'features'])

        dedicatedfws = filter(lambda x: x['dedicatedFirewallFlag'], fwvlans)
        for vlan in dedicatedfws:
            features = []
            if vlan['highAvailabilityFirewallFlag']:
                features.append('HA')

            if features:
                feature_list = listing(features, separator=',')
            else:
                feature_list = blank()

            t.add_row([
                vlan['vlanNumber'],
                'dedicated',
                feature_list,
            ])

        shared_vlan = filter(lambda x: not x['dedicatedFirewallFlag'], fwvlans)
        for vlan in shared_vlan:
            t.add_row([vlan['vlanNumber'], 'standard', blank()])

        return t
