#!/usr/bin/env python

from SoftLayer.CLI import CLIRunnable
from SoftLayer.firewall import FirewallManager

__doc__ = "Firewall rule and security management"


class FWList(CLIRunnable):
    """ List active vlans with firewalls """
    action = 'list'

    @staticmethod
    def execute(client, args):
        f = FirewallManager(client)
        vlans = f.list()['networkVlans']
        fwvlans = filter(has_firewall, vlans)

        if any(lambda x: x['dedicatedFirewallFlag'] for x in fwvlans):
            print "Dedicated firewalls"
            for vlan in filter(
                    lambda x: x['dedicatedFirewallFlag'], fwvlans):
                print("{0[vlanNumber]} "
                      "HA:{0[highAvailabilityFirewallFlag]}".format(vlan))

        shared_vlan = filter(lambda x: not x['dedicatedFirewallFlag'], fwvlans)
        if shared_vlan:
            print "Shared firewall vlans"
            for vlan in shared_vlan:
                print("{0[vlanNumber]} ".format(vlan))


def has_firewall(vlan):
    return bool(
        vlan['dedicatedFirewallFlag'] or
        vlan['highAvailabilityFirewallFlag'] or
        vlan['firewallInterfaces'] or
        vlan['firewallNetworkComponents'] or
        vlan['firewallGuestNetworkComponents']
    )
