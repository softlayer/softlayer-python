"""Display details for a specified volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@click.argument('volume_id')
@environment.pass_env
def cli(env, volume_id):
    """Display details for a specified volume."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    block_volume = block_manager.get_block_volume_details(volume_id)
    block_volume = utils.NestedDict(block_volume)

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    storage_type = block_volume['storageType']['keyName'].split('_').pop(0)
    table.add_row(['ID', block_volume['id']])
    table.add_row(['Username', block_volume['username']])
    table.add_row(['Type', storage_type])
    table.add_row(['Capacity (GB)', "%iGB" % block_volume['capacityGb']])
    table.add_row(['LUN Id', "%s" % block_volume['lunId']])

    if block_volume.get('iops'):
        table.add_row(['IOPs', block_volume['iops']])

    if block_volume.get('storageTierLevel'):
        table.add_row([
            'Endurance Tier',
            block_volume['storageTierLevel']['description'],
        ])

    table.add_row([
        'Data Center',
        block_volume['serviceResource']['datacenter']['name'],
    ])
    table.add_row([
        'Target IP',
        block_volume['serviceResourceBackendIpAddress'],
    ])

    if block_volume['snapshotCapacityGb']:
        table.add_row([
            'Snapshot Capacity (GB)',
            block_volume['snapshotCapacityGb'],
        ])
        table.add_row([
            'Snapshot Used (Bytes)',
            block_volume['parentVolume']['snapshotSizeBytes'],
        ])

    env.fout(table)
