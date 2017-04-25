"""List suitable replication datacenters for the given volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

COLUMNS = [
    column_helper.Column('ID', ('id',), mask="id"),
    column_helper.Column('Long Name', ('longName',), mask="longName"),
    column_helper.Column('Short Name', ('name',), mask="name"),
]

DEFAULT_COLUMNS = [
    'ID',
    'Long Name',
    'Short Name',
]


@click.command()
@click.argument('volume-id')
@click.option('--sortby', help='Column to sort by', default='Long Name')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. Options: {0}'.format(
                  ', '.join(column.name for column in COLUMNS)),
              default=','.join(DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, columns, sortby, volume_id):
    """List suitable replication datacenters for the given volume."""
    file_storage_manager = SoftLayer.FileStorageManager(env.client)

    legal_centers = file_storage_manager.get_replication_locations(
        volume_id
    )

    if not legal_centers:
        click.echo("No data centers compatible for replication.")
    else:
        table = formatting.KeyValueTable(columns.columns)
        table.sortby = sortby
        for legal_center in legal_centers:
            table.add_row([value or formatting.blank()
                           for value in columns.row(legal_center)])

        env.fout(table)
