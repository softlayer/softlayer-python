"""List firewalls."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):
    """List firewalls."""

    mgr = SoftLayer.FirewallManager(env.client)
    table = formatting.Table(['firewall id',
                              'type',
                              'features',
                              'server/vlan id'])
    fwvlans = mgr.get_firewalls()
    dedicated_firewalls = [firewall for firewall in fwvlans
                           if firewall['dedicatedFirewallFlag']]

    for vlan in dedicated_firewalls:
        features = []
        if vlan['highAvailabilityFirewallFlag']:
            features.append('HA')

        if features:
            feature_list = formatting.listing(features, separator=',')
        else:
            feature_list = formatting.blank()

        table.add_row([
            'vlan:%s' % vlan['networkVlanFirewall']['id'],
            'VLAN - dedicated',
            feature_list,
            vlan['id']
        ])

    shared_vlan = [firewall for firewall in fwvlans
                   if not firewall['dedicatedFirewallFlag']]
    for vlan in shared_vlan:
        vs_firewalls = [guest
                        for guest in vlan['firewallGuestNetworkComponents']
                        if has_firewall_component(guest)]

        for firewall in vs_firewalls:
            table.add_row([
                'vs:%s' % firewall['id'],
                'Virtual Server - standard',
                '-',
                firewall['guestNetworkComponent']['guest']['id']
            ])

        server_firewalls = [server
                            for server in vlan['firewallNetworkComponents']
                            if has_firewall_component(server)]

        for firewall in server_firewalls:
            table.add_row([
                'server:%s' % firewall['id'],
                'Server - standard',
                '-',
                utils.lookup(firewall,
                             'networkComponent',
                             'downlinkComponent',
                             'hardwareId')
            ])

    env.fout(table)


def has_firewall_component(server):
    """Helper to determine whether or not a server has a firewall.

    :param dict server: A dictionary representing a server
    :returns: True if the Server has a firewall.
    """
    if server['status'] != 'no_edit':
        return True

    return False
