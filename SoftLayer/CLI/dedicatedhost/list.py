"""List dedicated servers."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

COLUMNS = [
    column_helper.Column('datacenter', ('datacenter', 'name')),
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
    'name',
    'cpuCount',
    'diskCapacity',
    'memoryCapacity',
    'datacenter',
    'guestCount',
]


@click.command()
@click.option('--cpu', '-c', help='Number of CPU cores', type=click.INT)
@helpers.multi_option('--tag', help='Filter by tags')
@click.option('--sortby', help='Column to sort by',
              default='name',
              show_default=True)
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. [options: %s]'
              % ', '.join(column.name for column in COLUMNS),
              default=','.join(DEFAULT_COLUMNS),
              show_default=True)
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--name', '-H', help='Host portion of the FQDN')
@click.option('--memory', '-m', help='Memory capacity in mebibytes',
              type=click.INT)
@click.option('--disk', '-D', help='Disk capacity')
@environment.pass_env
def cli(env, sortby, cpu, columns, datacenter, name, memory, disk, tag):
    """List dedicated host."""
    mgr = SoftLayer.DedicatedHostManager(env.client)
    hosts = mgr.list_instances(cpus=cpu,
                               datacenter=datacenter,
                               hostname=name,
                               memory=memory,
                               disk=disk,
                               tags=tag,
                               mask=columns.mask())

    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for host in hosts:
        table.add_row([value or formatting.blank()
                       for value in columns.row(host)])

    env.fout(table)
