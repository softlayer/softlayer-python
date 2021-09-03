"""List existing replicant volumes for a file volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import storage_utils

COLUMNS = storage_utils.REPLICATION_PARTNER_COLUMNS
DEFAULT_COLUMNS = storage_utils.REPLICATION_PARTNER_DEFAULT


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
