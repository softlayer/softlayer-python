"""List hardware servers."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


import click


@click.command()
@click.option('--sortby', help='Column to sort by',
              default='hostname')
@click.option('--cpu', '-c', help='Filter by number of CPU cores')
@click.option('--domain', '-D', help='Filter by domain')
@click.option('--datacenter', '-d', help='Filter by datacenter')
@click.option('--hostname', '-H', help='Filter by hostname')
@click.option('--memory', '-m', help='Filter by memory in gigabytes')
@click.option('--network', '-n', help='Filter by network port speed in Mbps')
@click.option('--columns', help='Columns to display. default is '
              ' id, hostname, primary_ip, backend_ip, datacenter, action',
              default="id,hostname,primary_ip,backend_ip,datacenter,action")
@helpers.multi_option('--tag', help='Filter by tags')
@environment.pass_env
def cli(env, sortby, cpu, domain, datacenter, hostname, memory, network, tag,
        columns):
    """List hardware servers."""

    manager = SoftLayer.HardwareManager(env.client)
    columns_clean = [col.strip() for col in columns.split(',')]

    servers = manager.list_hardware(hostname=hostname,
                                    domain=domain,
                                    cpus=cpu,
                                    memory=memory,
                                    datacenter=datacenter,
                                    nic_speed=network,
                                    tags=tag)

    table = formatting.Table(columns_clean)
    table.sortby = sortby
    column_map = {}
    column_map['guid'] = 'globalIdentifier'
    column_map['primary_ip'] = 'primaryIpAddress'
    column_map['backend_ip'] = 'primaryBackendIpAddress'
    column_map['datacenter'] = 'datacenter-name'
    column_map['action'] = 'formatted-action'
    column_map['powerState'] = 'powerState-name'

    for server in servers:
        server = utils.NestedDict(server)
        server['datacenter-name'] = server['datacenter']['name']
        server['formatted-action'] = formatting.active_txn(server)
        server['powerState-name'] = server['powerState']['name']
        row_column = []
        for col in columns_clean:
            entry = None
            if col in column_map:
                entry = server[column_map[col]]
            else:
                entry = server[col]

            row_column.append(entry or formatting.blank())

        table.add_row(row_column)

    env.fout(table)
