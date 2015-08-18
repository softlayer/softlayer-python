"""List virtual servers."""
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
    'action': lambda guest: formatting.active_txn(guest),
    'power_state': ('powerState', 'name'),
}


@click.command()
@click.option('--sortby', help='Column to sort by', default='hostname')
@click.option('--cpu', '-c', help='Number of CPU cores', type=click.INT)
@click.option('--domain', '-D', help='Domain portion of the FQDN')
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--hostname', '-H', help='Host portion of the FQDN')
@click.option('--memory', '-m', help='Memory in mebibytes', type=click.INT)
@click.option('--network', '-n', help='Network port speed in Mbps')
@click.option('--hourly', is_flag=True, help='Show only hourly instances')
@click.option('--monthly', is_flag=True, help='Show only monthly instances')
@helpers.multi_option('--tag', help='Filter by tags')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMN_MAP),
              help='Columns to display. default is id, hostname, primary_ip, '
              'backend_ip, datacenter, action',
              default="id,hostname,primary_ip,backend_ip,datacenter,action")
@environment.pass_env
def cli(env, sortby, cpu, domain, datacenter, hostname, memory, network,
        hourly, monthly, tag, columns):
    """List virtual servers."""

    vsi = SoftLayer.VSManager(env.client)
    guests = vsi.list_instances(hourly=hourly,
                                monthly=monthly,
                                hostname=hostname,
                                domain=domain,
                                cpus=cpu,
                                memory=memory,
                                datacenter=datacenter,
                                nic_speed=network,
                                tags=tag)

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for guest in guests:
        table.add_row([value or formatting.blank()
                       for value in columns.row(guest)])

    env.fout(table)
