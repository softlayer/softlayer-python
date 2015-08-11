"""List virtual servers."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

import click


@click.command()
@click.option('--sortby', help='Column to sort by',
              default='hostname')
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
@click.option('--columns', help='Columns to display. default is '
              ' guid, hostname, primary_ip, backend_ip, datacenter, action',
              default="guid,hostname,primary_ip,backend_ip,datacenter,action")
@environment.pass_env
def cli(env, sortby, cpu, domain, datacenter, hostname, memory, network,
        hourly, monthly, tags, columns):
    """List virtual servers."""

    vsi = SoftLayer.VSManager(env.client)
    columns_clean = [col.strip() for col in columns.split(',')]
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

    table = formatting.Table(columns_clean)
    table.sortby = sortby
    column_map = {}
    column_map['guid'] = 'globalIdentifier'
    column_map['primary_ip'] = 'primaryIpAddress'
    column_map['backend_ip'] = 'primaryBackendIpAddress'
    column_map['datacenter'] = 'datacenter-name'
    column_map['action'] = 'formatted-action'
    column_map['powerState'] = 'powerState-name'

    for guest in guests:
        guest = utils.NestedDict(guest)
        guest['datacenter-name'] = guest['datacenter']['name']
        guest['formatted-action'] = formatting.active_txn(guest)
        guest['powerState-name'] = guest['powerState']['name']
        row_column = []
        for col in columns_clean:
            entry = None
            if col in column_map:
                entry = guest[column_map[col]]
            else:
                entry = guest[col]

            row_column.append(entry or formatting.blank())

        table.add_row(row_column)

    return table
