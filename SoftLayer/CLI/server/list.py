"""List hardware servers."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

import click

# pylint: disable=unnecessary-lambda

COLUMN_MAP = {
    'guid': ('globalIdentifier',),
    'primary_ip': ('primaryIpAddress',),
    'backend_ip': ('primaryBackendIpAddress',),
    'datacenter': ('datacenter', 'name'),
    'action': lambda server: formatting.active_txn(server),
    'power_state': ('powerState', 'name'),
}


@click.command()
@click.option('--sortby', help='Column to sort by', default='hostname')
@click.option('--cpu', '-c', help='Filter by number of CPU cores')
@click.option('--domain', '-D', help='Filter by domain')
@click.option('--datacenter', '-d', help='Filter by datacenter')
@click.option('--hostname', '-H', help='Filter by hostname')
@click.option('--memory', '-m', help='Filter by memory in gigabytes')
@click.option('--network', '-n', help='Filter by network port speed in Mbps')
@helpers.multi_option('--tag', help='Filter by tags')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMN_MAP),
              help='Columns to display. default is id, hostname, primary_ip, '
              'backend_ip, datacenter, action',
              default="id,hostname,primary_ip,backend_ip,datacenter,action")
@environment.pass_env
def cli(env, sortby, cpu, domain, datacenter, hostname, memory, network, tag,
        columns):
    """List hardware servers."""

    manager = SoftLayer.HardwareManager(env.client)

    servers = manager.list_hardware(hostname=hostname,
                                    domain=domain,
                                    cpus=cpu,
                                    memory=memory,
                                    datacenter=datacenter,
                                    nic_speed=network,
                                    tags=tag)

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for server in servers:
        table.add_row([value or formatting.blank()
                       for value in columns.row(server)])

    env.fout(table)
