"""Get subnet details."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--no-vs',
              is_flag=True,
              help="Hide virtual server listing")
@click.option('--no-hardware',
              is_flag=True,
              help="Hide hardware listing")
@environment.pass_env
def cli(env, identifier, no_vs, no_hardware):
    """Get subnet details."""

    mgr = SoftLayer.NetworkManager(env.client)
    subnet_id = helpers.resolve_id(mgr.resolve_subnet_ids, identifier,
                                   name='subnet')
    subnet = mgr.get_subnet(subnet_id)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', subnet['id']])
    table.add_row(['identifier',
                   '%s/%s' % (subnet['networkIdentifier'],
                              str(subnet['cidr']))])
    table.add_row(['subnet type', subnet['subnetType']])
    table.add_row(['gateway', subnet.get('gateway', formatting.blank())])
    table.add_row(['broadcast',
                   subnet.get('broadcastAddress', formatting.blank())])
    table.add_row(['datacenter', subnet['datacenter']['name']])
    table.add_row(['usable ips',
                   subnet.get('usableIpAddressCount', formatting.blank())])

    if not no_vs:
        if subnet['virtualGuests']:
            vs_table = formatting.Table(['Hostname', 'Domain', 'IP'])
            vs_table.align['Hostname'] = 'r'
            vs_table.align['IP'] = 'l'
            for vsi in subnet['virtualGuests']:
                vs_table.add_row([vsi['hostname'],
                                  vsi['domain'],
                                  vsi.get('primaryIpAddress')])
            table.add_row(['vs', vs_table])
        else:
            table.add_row(['vs', 'none'])

    if not no_hardware:
        if subnet['hardware']:
            hw_table = formatting.Table(['Hostname', 'Domain', 'IP'])
            hw_table.align['Hostname'] = 'r'
            hw_table.align['IP'] = 'l'
            for hardware in subnet['hardware']:
                hw_table.add_row([hardware['hostname'],
                                  hardware['domain'],
                                  hardware.get('primaryIpAddress')])
            table.add_row(['hardware', hw_table])
        else:
            table.add_row(['hardware', 'none'])

    env.fout(table)
