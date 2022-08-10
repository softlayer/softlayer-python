"""Get details about a VLAN."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--no-vs',
              is_flag=True,
              help="Hide virtual server listing")
@click.option('--no-hardware',
              is_flag=True,
              help="Hide hardware listing")
@click.option('--no-trunks',
              is_flag=True,
              help="Hide devices with trunks")
@environment.pass_env
def cli(env, identifier, no_vs, no_hardware, no_trunks):
    """Get details about a VLAN."""
    mgr = SoftLayer.NetworkManager(env.client)

    vlan_id = helpers.resolve_id(mgr.resolve_vlan_ids, identifier, 'VLAN')

    mask = """mask[firewallInterfaces,primaryRouter[id, fullyQualifiedDomainName, datacenter],
    totalPrimaryIpAddressCount,networkSpace,billingItem,hardware,subnets,virtualGuests,
    networkVlanFirewall[id,fullyQualifiedDomainName,primaryIpAddress],attachedNetworkGateway[id,name,networkFirewall],
    networkComponentTrunks[networkComponent[downlinkComponent[networkComponentGroup[membersDescription],
    hardware[tagReferences]]]]]"""

    vlan = mgr.get_vlan(vlan_id, mask=mask)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', vlan.get('id')])
    table.add_row(['number', vlan.get('vlanNumber')])
    table.add_row(['datacenter',
                   utils.lookup(vlan, 'primaryRouter', 'datacenter', 'longName')])
    table.add_row(['primary_router',
                   utils.lookup(vlan, 'primaryRouter', 'fullyQualifiedDomainName')])
    table.add_row(['Gateway/Firewall', get_gateway_firewall(vlan)])

    if vlan.get('subnets'):
        subnet_table = formatting.Table(['id', 'identifier', 'netmask', 'gateway', 'type', 'usable ips'])
        for subnet in vlan.get('subnets'):
            subnet_table.add_row([subnet.get('id'),
                                  subnet.get('networkIdentifier'),
                                  subnet.get('netmask'),
                                  subnet.get('gateway') or formatting.blank(),
                                  subnet.get('subnetType'),
                                  subnet.get('usableIpAddressCount')])
        # subnets.append(subnet_table)
        table.add_row(['subnets', subnet_table])
    else:
        table.add_row(['subnets', '-'])

    server_columns = ['hostname', 'domain', 'public_ip', 'private_ip']

    if not no_vs:
        if vlan.get('virtualGuests'):
            vs_table = formatting.KeyValueTable(server_columns)
            for vsi in vlan['virtualGuests']:
                vs_table.add_row([vsi.get('hostname'),
                                  vsi.get('domain'),
                                  vsi.get('primaryIpAddress'),
                                  vsi.get('primaryBackendIpAddress')])
            table.add_row(['vs', vs_table])
        else:
            table.add_row(['vs', '-'])

    if not no_hardware:
        if vlan.get('hardware'):
            hw_table = formatting.Table(server_columns)
            for hardware in vlan['hardware']:
                hw_table.add_row([hardware.get('hostname'),
                                  hardware.get('domain'),
                                  hardware.get('primaryIpAddress'),
                                  hardware.get('primaryBackendIpAddress')])
            table.add_row(['hardware', hw_table])
        else:
            table.add_row(['hardware', '-'])

    if not no_trunks:
        if vlan.get('networkComponentTrunks'):
            trunks = filter_trunks(vlan.get('networkComponentTrunks'))
            trunks_table = formatting.Table(['device', 'port', 'tags'])
            for trunk in trunks:
                trunks_table.add_row([utils.lookup(trunk, 'networkComponent', 'downlinkComponent',
                                                   'hardware', 'fullyQualifiedDomainName'),
                                      utils.lookup(trunk, 'networkComponent', 'downlinkComponent',
                                                   'networkComponentGroup', 'membersDescription'),
                                      formatting.tags(utils.lookup(trunk, 'networkComponent', 'downlinkComponent',
                                                                   'hardware', 'tagReferences'))])
            table.add_row(['trunks', trunks_table])
        else:
            table.add_row(['trunks', '-'])

    env.fout(table)


def get_gateway_firewall(vlan):
    """Gets the name of a gateway/firewall from a VLAN. """

    firewall = utils.lookup(vlan, 'networkVlanFirewall', 'fullyQualifiedDomainName')
    if firewall:
        return firewall
    gateway = utils.lookup(vlan, 'attachedNetworkGateway', 'name')
    if gateway:
        return gateway
    return formatting.blank()


def filter_trunks(trunks):
    """Filter duplicates devices with trunks of the vlan."""
    trunk_filters = []
    hardware_id = []
    for trunk in trunks:
        if utils.lookup(trunk, 'networkComponent', 'downlinkComponent', 'hardwareId') not in hardware_id:
            trunk_filters.append(trunk)
            hardware_id.append(utils.lookup(trunk, 'networkComponent', 'downlinkComponent', 'hardwareId'))
    return trunk_filters
