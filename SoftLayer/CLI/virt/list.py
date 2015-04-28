"""List virtual servers."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

import click


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(['guid',
                                 'hostname',
                                 'primary_ip',
                                 'backend_ip',
                                 'datacenter']))
@click.option('--cpu', '-c', help='Number of CPU cores', type=click.INT)
@click.option('--domain', '-D', help='Domain portion of the FQDN')
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--hostname', '-H', help='Host portion of the FQDN')
@click.option('--memory', '-m', help='Memory in mebibytes', type=click.INT)
@click.option('--network', '-n', help='Network port speed in Mbps')
@click.option('--hourly', is_flag=True, help='Show only hourly instances')
@click.option('--monthly', is_flag=True, help='Show only monthly instances')
@click.option('--tags',
              help='Show instances that have one of these comma-separated '
                   'tags')
@environment.pass_env
def cli(env, sortby, cpu, domain, datacenter, hostname, memory, network,
        hourly, monthly, tags):
    """List virtual servers."""

    vsi = SoftLayer.VSManager(env.client)

    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]

    guests = vsi.list_instances(hourly=hourly,
                                monthly=monthly,
                                hostname=hostname,
                                domain=domain,
                                cpus=cpu,
                                memory=memory,
                                datacenter=datacenter,
                                nic_speed=network,
                                tags=tag_list)

    table = formatting.Table([
        'id',
        'hostname',
        'primary_ip',
        'backend_ip',
        'datacenter',
        'action',
    ])
    table.sortby = sortby or 'hostname'

    for guest in guests:
        table.add_row([
            utils.lookup(guest, 'id'),
            utils.lookup(guest, 'hostname') or formatting.blank(),
            utils.lookup(guest, 'primaryIpAddress') or formatting.blank(),
            utils.lookup(guest, 'primaryBackendIpAddress') or
            formatting.blank(),
            utils.lookup(guest, 'datacenter', 'name') or formatting.blank(),
            formatting.active_txn(guest),
        ])

    return table
