"""Display details for a specified volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume_id')
@environment.pass_env
def cli(env, volume_id):
    """Display details for a specified volume."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    block_volume_id = helpers.resolve_id(block_manager.resolve_ids, volume_id, 'Block Volume')
    block_volume = block_manager.get_block_volume_details(block_volume_id)
    block_volume = utils.NestedDict(block_volume)

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    capacity = '0'
    if block_volume['capacityGb'] != '':
        capacity = "%iGB" % block_volume['capacityGb']
    storage_type = block_volume['storageType']['keyName'].split('_').pop(0)
    table.add_row(['ID', block_volume['id']])
    table.add_row(['Username', block_volume['username']])
    table.add_row(['Type', storage_type])
    table.add_row(['Capacity (GB)', capacity])
    table.add_row(['LUN Id', block_volume['lunId']])

    if block_volume.get('provisionedIops'):
        table.add_row(['IOPs', block_volume['provisionedIops']])

    if block_volume.get('storageTierLevel'):
        table.add_row(['Endurance Tier', block_volume['storageTierLevel']])

    table.add_row(['Data Center', block_volume['serviceResource']['datacenter']['name']])
    table.add_row(['Target IP', block_volume['serviceResourceBackendIpAddress']])

    if block_volume['snapshotCapacityGb']:
        table.add_row(['Snapshot Capacity (GB)', block_volume['snapshotCapacityGb']])
        if 'snapshotSizeBytes' in block_volume['parentVolume']:
            table.add_row(['Snapshot Used (Bytes)', block_volume['parentVolume']['snapshotSizeBytes']])

    table.add_row(['# of Active Transactions', block_volume['activeTransactionCount']])

    if block_volume['activeTransactions']:
        for trans in block_volume['activeTransactions']:
            if 'transactionStatus' in trans and 'friendlyName' in trans['transactionStatus']:
                table.add_row(['Ongoing Transaction', trans['transactionStatus']['friendlyName']])

    table.add_row(['Replicant Count', block_volume.get('replicationPartnerCount', 0)])

    if block_volume['replicationPartnerCount'] > 0:
        # This if/else temporarily handles a bug in which the SL API
        # returns a string or object for 'replicationStatus'; it seems that
        # the type is string for File volumes and object for Block volumes
        if 'message' in block_volume['replicationStatus']:
            table.add_row(['Replication Status', block_volume['replicationStatus']['message']])
        else:
            table.add_row(['Replication Status', block_volume['replicationStatus']])

        replicant_table = formatting.Table(['Id', 'Username', 'Target', 'Location', 'Schedule'])
        replicant_table.align['Name'] = 'r'
        replicant_table.align['Value'] = 'l'
        for replicant in block_volume['replicationPartners']:
            replicant_table.add_row([
                replicant.get('id'),
                utils.lookup(replicant, 'username'),
                utils.lookup(replicant, 'serviceResourceBackendIpAddress'),
                utils.lookup(replicant, 'serviceResource', 'datacenter', 'name'),
                utils.lookup(replicant, 'replicationSchedule', 'type', 'keyname')
            ])
        table.add_row(['Replicant Volumes', replicant_table])

    if block_volume.get('originalVolumeSize'):
        original_volume_info = formatting.Table(['Property', 'Value'])
        original_volume_info.add_row(['Original Volume Size', block_volume['originalVolumeSize']])
        if block_volume.get('originalVolumeName'):
            original_volume_info.add_row(['Original Volume Name', block_volume['originalVolumeName']])
        if block_volume.get('originalSnapshotName'):
            original_volume_info.add_row(['Original Snapshot Name', block_volume['originalSnapshotName']])
        table.add_row(['Original Volume Properties', original_volume_info])

    notes = f"{block_volume.get('notes', '')}"
    table.add_row(['Notes', notes])

    env.fout(table)
