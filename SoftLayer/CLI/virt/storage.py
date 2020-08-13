"""Get storage details for a virtual server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get storage details for a virtual server."""

    vsi = SoftLayer.VSManager(env.client)
    vsi_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    iscsi_storage_data = vsi.get_storage_details(vsi_id, "ISCSI")
    nas_storage_data = vsi.get_storage_details(vsi_id, "NAS")
    storage_credentials = vsi.get_storage_credentials(vsi_id)
    portable_storage = vsi.get_portable_storage(vsi_id)
    local_disks = vsi.get_local_disks(vsi_id)

    table_credentials = formatting.Table(['Username', 'Password', 'IQN'], title="Block Storage Details \n iSCSI")
    if storage_credentials:
        table_credentials.add_row([storage_credentials['credential']['username'],
                                   storage_credentials['credential']['password'],
                                   storage_credentials['name']])

    table_iscsi = formatting.Table(['LUN name', 'capacity', 'Target address', 'Location', 'Notes'])
    for iscsi in iscsi_storage_data:
        table_iscsi.add_row([iscsi['username'], iscsi['capacityGb'],
                             iscsi['serviceResourceBackendIpAddress'],
                             iscsi['allowedVirtualGuests'][0]['datacenter']['longName'],
                             iscsi.get('notes', None)])

    table_portable = formatting.Table(['Description', 'Capacity'], title="Portable Storage")
    for portable in portable_storage:
        table_portable.add_row([portable.get('description', None), portable.get('capacity', None)])

    table_nas = formatting.Table(['Volume name', 'capacity', 'Host Name', 'Location', 'Notes'],
                                 title="File Storage Details")
    for nas in nas_storage_data:
        table_nas.add_row([nas['username'], nas['capacityGb'],
                           nas['serviceResourceBackendIpAddress'],
                           nas['allowedVirtualGuests'][0]['datacenter']['longName'],
                           nas.get('notes', None)])

    table_local_disks = get_local_storage_table(local_disks)
    table_local_disks.title = "Other storage details"

    env.fout(table_credentials)
    env.fout(table_iscsi)
    env.fout(table_portable)
    env.fout(table_nas)
    env.fout(table_local_disks)


def get_local_type(disks):
    """Returns the virtual server local disk type.

    :param disks: virtual server local disks.
    """
    disk_type = 'System'
    if 'SWAP' in disks.get('diskImage', {}).get('description', []):
        disk_type = 'Swap'

    return disk_type


def get_local_storage_table(local_disks):
    """Returns a formatting local disk table

      :param local_disks: virtual server local disks.
      """
    table_local_disks = formatting.Table(['Type', 'Name', 'Drive', 'Capacity'])
    for disk in local_disks:
        if 'diskImage' in disk:
            table_local_disks.add_row([
                get_local_type(disk),
                disk['mountType'],
                disk['device'],
                "{capacity} {unit}".format(capacity=disk['diskImage']['capacity'],
                                           unit=disk['diskImage']['units'])
            ])
    return table_local_disks
