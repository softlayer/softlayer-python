"""Get status for split or move completed percentage of a given block duplicate volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand,
               epilog="""Get status for split or move completed percentage of a given block duplicate volume.""")
@click.argument('volume-id')
@environment.pass_env
def cli(env, volume_id):
    """Get status for split or move completed percentage of a given block duplicate volume."""
    table = formatting.Table(['username', 'active_conversion_start_time', 'completed_percentage'])

    block_manager = SoftLayer.BlockStorageManager(env.client)

    value = block_manager.split_percentage(
        volume_id
    )

    table.add_row(
        [
            value['volumeUsername'],
            value['activeConversionStartTime'],
            value['deDuplicateConversionPercentage']
        ]
    )

    env.fout(table)



