"""List virtual servers."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


# pylint: disable=unnecessary-lambda

COLUMNS = [
    column_helper.Column('guid', ('globalIdentifier',)),
    column_helper.Column('primary_ip', ('primaryIpAddress',)),
    column_helper.Column('backend_ip', ('primaryBackendIpAddress',)),
    column_helper.Column('datacenter', ('datacenter', 'name')),
    column_helper.Column('action', lambda guest: formatting.active_txn(guest),
                         mask='''
                         activeTransaction[
                            id,transactionStatus[name,friendlyName]
                         ]'''),
    column_helper.Column('power_state', ('powerState', 'name')),
    column_helper.Column(
        'created_by',
        ('billingItem', 'orderItem', 'order', 'userRecord', 'username')),
    column_helper.Column(
        'tags',
        lambda server: formatting.tags(server.get('tagReferences')),
        mask="tagReferences.tag.name"),
]

DEFAULT_COLUMNS = [
    'id',
    'hostname',
    'primary_ip',
    'backend_ip',
    'datacenter',
    'action',
]


@click.command()
@click.option('--cpu', '-c', help='Number of CPU cores', type=click.INT)
@click.option('--domain', '-D', help='Domain portion of the FQDN')
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--hostname', '-H', help='Host portion of the FQDN')
@click.option('--memory', '-m', help='Memory in mebibytes', type=click.INT)
@click.option('--network', '-n', help='Network port speed in Mbps')
@click.option('--hourly', is_flag=True, help='Show only hourly instances')
@click.option('--monthly', is_flag=True, help='Show only monthly instances')
@helpers.multi_option('--tag', help='Filter by tags')
@click.option('--sortby',
              help='Column to sort by',
              default='hostname',
              show_default=True)
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. [options: %s]'
              % ', '.join(column.name for column in COLUMNS),
              default=','.join(DEFAULT_COLUMNS),
              show_default=True)
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
                                tags=tag,
                                mask=columns.mask())

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for guest in guests:
        table.add_row([value or formatting.blank()
                       for value in columns.row(guest)])

    env.fout(table)
