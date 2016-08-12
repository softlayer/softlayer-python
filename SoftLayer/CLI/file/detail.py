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
    file_manager = SoftLayer.FileStorageManager(env.client)
    file_volume = file_manager.get_file_volume_details(volume_id)
    file_volume = utils.NestedDict(file_volume)
    used_space = int(file_volume['bytesUsed'])

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    storage_type = file_volume['storageType']['keyName'].split('_').pop(0)
    table.add_row(['ID', file_volume['id']])
    table.add_row(['Username', file_volume['username']])
    table.add_row(['Type', storage_type])
    table.add_row(['Capacity (GB)', "%iGB" % file_volume['capacityGb']])

    if used_space < (1 << 10):
        table.add_row(['Used Space', "%dB" % used_space])
    elif used_space < (1 << 20):
        table.add_row(['Used Space', "%dKB" % (used_space / (1 << 10))])
    elif used_space < (1 << 30):
        table.add_row(['Used Space', "%dMB" % (used_space / (1 << 20))])
    else:
        table.add_row(['Used Space', "%dGB" % (used_space / (1 << 30))])

    if file_volume.get('iops'):
        table.add_row(['IOPs', file_volume['iops']])

    if file_volume.get('storageTierLevel'):
        table.add_row([
            'Endurance Tier',
            file_volume['storageTierLevel']['description'],
        ])

    table.add_row([
        'Data Center',
        file_volume['serviceResource']['datacenter']['name'],
    ])
    table.add_row([
        'Target IP',
        file_volume['serviceResourceBackendIpAddress'],
    ])

    if file_volume['snapshotCapacityGb']:
        table.add_row([
            'Snapshot Capacity (GB)',
            file_volume['snapshotCapacityGb'],
        ])
        if 'snapshotSizeBytes' in file_volume['parentVolume']:
            table.add_row([
                'Snapshot Used (Bytes)',
                file_volume['parentVolume']['snapshotSizeBytes'],
            ])

    table.add_row(['# of Active Transactions', "%i"
                   % file_volume['activeTransactionCount']])

    if file_volume['activeTransactions']:
        for trans in file_volume['activeTransactions']:
            table.add_row([
                'Ongoing Transactions',
                trans['transactionStatus']['friendlyName']])

    env.fout(table)
