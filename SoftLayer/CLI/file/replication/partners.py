"""List existing replicant volumes for a file volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

COLUMNS = [
    column_helper.Column('ID', ('id',)),
    column_helper.Column('Username', ('username',), mask="username"),
    column_helper.Column('Account ID', ('accountId',), mask="accountId"),
    column_helper.Column('Capacity (GB)', ('capacityGb',), mask="capacityGb"),
    column_helper.Column('Hardware ID', ('hardwareId',), mask="hardwareId"),
    column_helper.Column('Guest ID', ('guestId',), mask="guestId"),
    column_helper.Column('Host ID', ('hostId',), mask="hostId"),
]

# In-line comment to avoid similarity flag with block version

DEFAULT_COLUMNS = [
    'ID',
    'Username',
    'Account ID',
    'Capacity (GB)',
    'Hardware ID',
    'Guest ID',
    'Host ID'
]


@click.command()
@click.argument('volume-id')
@click.option('--sortby', help='Column to sort by', default='Username')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. Options: {0}'.format(
                  ', '.join(column.name for column in COLUMNS)),
              default=','.join(DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, columns, sortby, volume_id):
    """List existing replicant volumes for a file volume."""
    file_storage_manager = SoftLayer.FileStorageManager(env.client)

    legal_volumes = file_storage_manager.get_replication_partners(
        volume_id
    )

    if not legal_volumes:
        click.echo("There are no replication partners for the given volume.")
    else:
        table = formatting.Table(columns.columns)
        table.sortby = sortby

        for legal_volume in legal_volumes:
            table.add_row([value or formatting.blank()
                           for value in columns.row(legal_volume)])

        env.fout(table)
