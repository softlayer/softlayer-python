"""Get subnet details."""
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
@environment.pass_env
def cli(env, identifier, no_vs, no_hardware):
    """Get subnet details."""

    mgr = SoftLayer.NetworkManager(env.client)
    subnet_id = helpers.resolve_id(mgr.resolve_subnet_ids, identifier,
                                   name='subnet')

    mask = 'mask[ipAddresses[id, ipAddress,note, hardware, virtualGuest], datacenter, virtualGuests, hardware,' \
           ' networkVlan[networkSpace,primaryRouter]]'

    subnet = mgr.get_subnet(subnet_id, mask=mask)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', subnet['id']])
    table.add_row(['identifier',
                   '%s/%s' % (subnet['networkIdentifier'],
                              str(subnet['cidr']))])
    table.add_row(['subnet type', subnet.get('subnetType', formatting.blank())])
    table.add_row(['network space',
                   utils.lookup(subnet, 'networkVlan', 'networkSpace')])
    table.add_row(['gateway', subnet.get('gateway', formatting.blank())])
    table.add_row(['broadcast',
                   subnet.get('broadcastAddress', formatting.blank())])
    table.add_row(['datacenter', subnet['datacenter']['name']])
    table.add_row(['usable ips',
                   subnet.get('usableIpAddressCount', formatting.blank())])
    table.add_row(['note',
                   subnet.get('note', formatting.blank())])
    table.add_row(['tags',
                   formatting.tags(subnet.get('tagReferences'))])

    ip_address = subnet.get('ipAddresses')

    ip_table = formatting.KeyValueTable(['id', 'ip', 'note'])
    for address in ip_address:
        description = '-'
        if address.get('hardware') is not None:
            description = address['hardware']['fullyQualifiedDomainName']
        elif address.get('virtualGuest') is not None:
            description = address['virtualGuest']['fullyQualifiedDomainName']
        ip_table.add_row([address.get('id'),
                          address.get('ipAddress') + '/' + description, address.get('note', '-')])

    table.add_row(['ipAddresses', ip_table])

    if not no_vs:
        if subnet['virtualGuests']:
            vs_table = formatting.Table(['hostname', 'domain', 'public_ip', 'private_ip'])
            for vsi in subnet['virtualGuests']:
                vs_table.add_row([vsi['hostname'],
                                  vsi['domain'],
                                  vsi.get('primaryIpAddress'),
                                  vsi.get('primaryBackendIpAddress')])
            table.add_row(['vs', vs_table])
        else:
            table.add_row(['vs', formatting.blank()])

    if not no_hardware:
        if subnet['hardware']:
            hw_table = formatting.Table(['hostname', 'domain', 'public_ip', 'private_ip'])
            for hardware in subnet['hardware']:
                hw_table.add_row([hardware['hostname'],
                                  hardware['domain'],
                                  hardware.get('primaryIpAddress'),
                                  hardware.get('primaryBackendIpAddress')])
            table.add_row(['hardware', hw_table])
        else:
            table.add_row(['hardware', formatting.blank()])

    env.fout(table)
