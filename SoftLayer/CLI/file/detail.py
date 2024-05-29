"""Display details for a specified volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


def get_capacity(file_volume):
    """Get the capacity Gb with validate the data"""
    capacity = '0'
    if file_volume['capacityGb'] != '':
        capacity = "%iGB" % file_volume['capacityGb']
    return capacity


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume_id')
@environment.pass_env
def cli(env, volume_id):
    """Display details for a specified volume."""
    file_manager = SoftLayer.FileStorageManager(env.client)
    file_volume_id = helpers.resolve_id(file_manager.resolve_ids, volume_id, 'File Storage')
    file_volume = file_manager.get_file_volume_details(file_volume_id)
    file_volume = utils.NestedDict(file_volume)

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    storage_type = file_volume['storageType']['keyName'].split('_').pop(0)
    table.add_row(['ID', file_volume['id']])
    table.add_row(['Username', file_volume['username']])
    table.add_row(['Type', storage_type])
    table.add_row(['Capacity (GB)', get_capacity(file_volume)])

    used_space = formatting.convert_sizes(file_volume.get('bytes_used', 0), "GB", False)
    table.add_row(['Used Space', used_space])

    if file_volume.get('provisionedIops'):
        table.add_row(['IOPs', file_volume['provisionedIops']])

    if file_volume.get('storageTierLevel'):
        table.add_row(['Endurance Tier', file_volume['storageTierLevel']])

    table.add_row(['Data Center', file_volume['serviceResource']['datacenter']['name']])
    table.add_row(['Target IP', file_volume['serviceResourceBackendIpAddress']])

    if file_volume['fileNetworkMountAddress']:
        table.add_row(['Mount Address', file_volume['fileNetworkMountAddress']])

    if file_volume['snapshotCapacityGb']:
        table.add_row(['Snapshot Capacity (GB)', file_volume['snapshotCapacityGb']])
        if 'snapshotSizeBytes' in file_volume['parentVolume']:
            table.add_row(['Snapshot Used (Bytes)', file_volume['parentVolume']['snapshotSizeBytes']])

    table.add_row(["# of Active Transactions", file_volume['activeTransactionCount']])

    if file_volume['activeTransactions']:
        for trans in file_volume['activeTransactions']:
            if 'transactionStatus' in trans and 'friendlyName' in trans['transactionStatus']:
                table.add_row(['Ongoing Transaction', trans['transactionStatus']['friendlyName']])

    table.add_row(['Replicant Count', "%u" % file_volume.get('replicationPartnerCount', 0)])

    if file_volume['replicationPartnerCount'] > 0:
        # This if/else temporarily handles a bug in which the SL API
        # returns a string or object for 'replicationStatus'; it seems that
        # the type is string for File volumes and object for Block volumes
        if 'message' in file_volume['replicationStatus']:
            table.add_row(['Replication Status', file_volume['replicationStatus']['message']])
        else:
            table.add_row(['Replication Status', file_volume['replicationStatus']])

        replicant_table = formatting.Table(['Id', 'Username', 'Target', 'Location', 'Schedule'])
        replicant_table.align['Name'] = 'r'
        replicant_table.align['Value'] = 'l'
        for replicant in file_volume['replicationPartners']:
            replicant_table.add_row([
                replicant.get('id'),
                utils.lookup(replicant, 'username'),
                utils.lookup(replicant, 'serviceResourceBackendIpAddress'),
                utils.lookup(replicant, 'serviceResource', 'datacenter', 'name'),
                utils.lookup(replicant, 'replicationSchedule', 'type', 'keyname')
            ])
        table.add_row(['Replicant Volumes', replicant_table])

    if file_volume.get('originalVolumeSize'):
        original_volume_info = formatting.Table(['Property', 'Value'])
        original_volume_info.add_row(['Original Volume Size', file_volume['originalVolumeSize']])
        if file_volume.get('originalVolumeName'):
            original_volume_info.add_row(['Original Volume Name', file_volume['originalVolumeName']])
        if file_volume.get('originalSnapshotName'):
            original_volume_info.add_row(['Original Snapshot Name', file_volume['originalSnapshotName']])
        table.add_row(['Original Volume Properties', original_volume_info])

    notes = f"{file_volume.get('notes', '')}"
    table.add_row(['Notes', notes])

    env.fout(table)
