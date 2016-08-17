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
        if 'snapshotSizeBytes' in block_volume['parentVolume']:
            table.add_row([
                'Snapshot Used (Bytes)',
                block_volume['parentVolume']['snapshotSizeBytes'],
            ])

    table.add_row(['# of Active Transactions', "%i"
                   % block_volume['activeTransactionCount']])

    if block_volume['activeTransactions']:
        for trans in block_volume['activeTransactions']:
            table.add_row([
                'Ongoing Transactions',
                trans['transactionStatus']['friendlyName']])

    table.add_row(['Replicant Count', "%u"
                   % block_volume['replicationPartnerCount']])

    if block_volume['replicationPartnerCount'] > 0:
        # This if/else temporarily handles a bug in which the SL API
        # returns a string or object for 'replicationStatus'; it seems that
        # the type is string for File volumes and object for Block volumes
        if 'message' in block_volume['replicationStatus']:
            table.add_row(['Replication Status', "%s"
                           % block_volume['replicationStatus']['message']])
        else:
            table.add_row(['Replication Status', "%s"
                           % block_volume['replicationStatus']])

        replicant_list = []
        for replicant in block_volume['replicationPartners']:
            replicant_table = formatting.Table(['Replicant ID',
                                                replicant['id']])
            replicant_table.add_row([
                'Volume Name',
                replicant['username']])
            replicant_table.add_row([
                'Target IP',
                replicant['serviceResourceBackendIpAddress']])
            replicant_table.add_row([
                'Data Center',
                replicant['serviceResource']['datacenter']['name']])
            replicant_table.add_row([
                'Schedule',
                replicant['replicationSchedule']['type']['keyname']])
            replicant_list.append(replicant_table)
        table.add_row(['Replicant Volumes', replicant_list])

    env.fout(table)
