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
@click.option('--column', help='Columns to display. default is '
              ' guid, hostname, primary_ip, backend_ip, datacenter, action',
              default="guid,hostname,primary_ip,backend_ip,datacenter,action")
@environment.pass_env
def cli(env, sortby, cpu, domain, datacenter, hostname, memory, network,
        hourly, monthly, tags, column):
    """List virtual servers."""

    vsi = SoftLayer.VSManager(env.client)
    columns = [col.strip() for col in column.split(',')]
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

    table = formatting.Table(columns)
    table.sortby = sortby or 'hostname'
    for guest in guests:
        guest = utils.NestedDict(guest)
        row_column = []
        for col in columns:
            entry = None
            if col == 'guid':
                entry = guest['globalIdentifier']
            elif col == 'datacenter':
                entry = guest['datacenter']['name']
            elif col == 'primary_ip':
                entry = guest['primaryIpAddress']
            elif col == 'backend_ip':
                entry = guest['primaryBackendIpAddress']
            elif col == 'action':
                entry = formatting.active_txn(guest)
            else:
                entry = guest[col]

            row_column.append(entry or formatting.blank())

        table.add_row(row_column)

    return table
