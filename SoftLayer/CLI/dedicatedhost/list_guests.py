"""List guests which are in a dedicated host server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

COLUMNS = [
    column_helper.Column('guid', ('globalIdentifier',)),
    column_helper.Column('cpu', ('maxCpu',)),
    column_helper.Column('memory', ('maxMemory',)),
    column_helper.Column('datacenter', ('datacenter', 'name')),
    column_helper.Column('primary_ip', ('primaryIpAddress',)),
    column_helper.Column('backend_ip', ('primaryBackendIpAddress',)),
    column_helper.Column(
        'created_by',
        ('billingItem', 'orderItem', 'order', 'userRecord', 'username')),
    column_helper.Column('power_state', ('powerState', 'name')),
    column_helper.Column(
        'tags',
        lambda server: formatting.tags(server.get('tagReferences')),
        mask="tagReferences.tag.name"),
]

DEFAULT_COLUMNS = [
    'id',
    'hostname',
    'domain',
    'primary_ip',
    'backend_ip',
    'power_state'
]


@click.command()
@click.argument('identifier')
@click.option('--cpu', '-c', help='Number of CPU cores', type=click.INT)
@click.option('--domain', '-D', help='Domain portion of the FQDN')
@click.option('--hostname', '-H', help='Host portion of the FQDN')
@click.option('--memory', '-m', help='Memory in mebibytes', type=click.INT)
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
def cli(env, identifier, sortby, cpu, domain, hostname, memory, tag, columns):
    """List guests which are in a dedicated host server."""

    mgr = SoftLayer.DedicatedHostManager(env.client)
    guests = mgr.list_guests(host_id=identifier,
                             cpus=cpu,
                             hostname=hostname,
                             domain=domain,
                             memory=memory,
                             tags=tag,
                             mask=columns.mask())

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for guest in guests:
        table.add_row([value or formatting.blank()
                       for value in columns.row(guest)])

    env.fout(table)
