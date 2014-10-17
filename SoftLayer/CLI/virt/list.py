"""List virtual servers"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

import click


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(['id',
                                 'datacenter',
                                 'host',
                                 'cores',
                                 'memory',
                                 'primary_ip',
                                 'backend_ip']))
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
    """List virtual servers"""

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
        'id', 'datacenter', 'host', 'cores', 'memory', 'primary_ip',
        'backend_ip', 'active_transaction', 'owner'
    ])
    table.sortby = sortby or 'host'

    for guest in guests:
        guest = utils.NestedDict(guest)
        table.add_row([
            guest['id'],
            guest['datacenter']['name'] or formatting.blank(),
            guest['fullyQualifiedDomainName'],
            guest['maxCpu'],
            formatting.mb_to_gb(guest['maxMemory']),
            guest['primaryIpAddress'] or formatting.blank(),
            guest['primaryBackendIpAddress'] or formatting.blank(),
            formatting.active_txn(guest),
            utils.lookup(guest, 'billingItem', 'orderItem', 'order',
                         'userRecord', 'username') or formatting.blank(),
        ])

    return table
