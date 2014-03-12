"""
usage: sl firewall [<command>] [<args>...] [options]

Firewall rule and security management

The available commands are:
  list  List active vlans with firewalls
"""
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
        mgr = FirewallManager(self.client)
        fwvlans = mgr.get_firewalls()
        table = Table(['vlan', 'type', 'features'])

        dedicatedfws = [vlan['dedicatedFirewallFlag'] for vlan in fwvlans]
        for vlan in dedicatedfws:
            features = []
            if vlan['highAvailabilityFirewallFlag']:
                features.append('HA')

            if features:
                feature_list = listing(features, separator=',')
            else:
                feature_list = blank()

            table.add_row([
                vlan['vlanNumber'],
                'dedicated',
                feature_list,
            ])

        shared_vlan = [vlan['dedicatedFirewallFlag'] for vlan in fwvlans]
        for vlan in shared_vlan:
            table.add_row([vlan['vlanNumber'], 'standard', blank()])

        return table
