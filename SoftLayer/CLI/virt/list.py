"""List virtual servers."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils

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
    column_helper.Column(
        'createDate',
        lambda guest: utils.clean_time(guest.get('createDate'),
                                       in_format='%Y-%m-%dT%H:%M:%S', out_format='%Y-%m-%d %H:%M'), mask="createDate"),
]

DEFAULT_COLUMNS = [
    'id',
    'hostname',
    'domain',
    'deviceStatus.name',
    'datacenter',
    'primary_ip',
    'backend_ip',
    'createDate',
    'action',
]


@click.command(cls=SLCommand, short_help="List virtual servers.")
@click.option('--cpu', '-c', help='Number of CPU cores', type=click.INT)
@click.option('--domain', '-D', help='Domain portion of the FQDN')
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--hostname', '-H', help='Host portion of the FQDN')
@click.option('--memory', '-m', help='Memory in mebibytes', type=click.INT)
@click.option('--network', '-n', help='Network port speed in Mbps')
@click.option('--hourly', is_flag=True, help='Show only hourly instances')
@click.option('--monthly', is_flag=True, help='Show only monthly instances')
@click.option('--tag', '-t', help='list of tags')
@click.option('--transient', help='Filter by transient instances', type=click.BOOL)
@click.option('--search', is_flag=False, flag_value="", default=None,
              help="Use the more flexible Search API to list instances. See `slcli search --types` for list " +
              "of searchable fields.")
@helpers.multi_option('--tag', help='Filter by tags')
@click.option('--sortby', default='hostname', show_default=True, help='Column to sort by')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. [options: %s]'
              % ', '.join(column.name for column in COLUMNS),
              default=','.join(DEFAULT_COLUMNS),
              show_default=True)
@click.option('--limit', '-l', default=100, show_default=True,
              help='How many results to get in one api call, default is 100')
@environment.pass_env
def cli(env, sortby, cpu, domain, datacenter, hostname, memory, network,
        hourly, monthly, tag, columns, limit, transient, search):
    """List virtual servers."""

    guests = []
    if search is not None:
        object_mask = f"mask[resource(SoftLayer_Virtual_Guest)[{columns.mask()}]]"
        search_manager = SoftLayer.SearchManager(env.client)
        guests = search_manager.search_instances(hostname=hostname, domain=domain, datacenter=datacenter,
                                                 tags=tag, search_string=search, mask=object_mask)
    else:
        vsi = SoftLayer.VSManager(env.client)
        guests = vsi.list_instances(hourly=hourly, monthly=monthly, hostname=hostname, domain=domain,
                                    cpus=cpu, memory=memory, datacenter=datacenter, nic_speed=network,
                                    transient=transient, tags=tag, mask=columns.mask(), limit=limit)

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for guest in guests:
        table.add_row([value or formatting.blank()
                       for value in columns.row(guest)])

    env.fout(table)
