"""Get storage details for a hardware server."""
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
    """Get storage details for a hardware server."""

    hardware = SoftLayer.HardwareManager(env.client)
    hardware_id = helpers.resolve_id(hardware.resolve_ids, identifier, 'hardware')
    iscsi_storage_data = hardware.get_storage_details(hardware_id, "ISCSI")
    nas_storage_data = hardware.get_storage_details(hardware_id, "NAS")
    storage_credentials = hardware.get_storage_credentials(hardware_id)
    hard_drives = hardware.get_hard_drives(hardware_id)

    table_credentials = formatting.Table(['Username', 'Password', 'IQN'], title="Block Storage Details \n iSCSI")
    if storage_credentials:
        table_credentials.add_row([storage_credentials['credential']['username'],
                                   storage_credentials['credential']['password'],
                                   storage_credentials['name']])

    table_iscsi = formatting.Table(['LUN name', 'capacity', 'Target address', 'Location', 'Notes'])
    for iscsi in iscsi_storage_data:
        table_iscsi.add_row([iscsi['username'], iscsi['capacityGb'],
                             iscsi['serviceResourceBackendIpAddress'],
                             iscsi['allowedHardware'][0]['datacenter']['longName'],
                             iscsi.get('notes', None)])

    table_nas = formatting.Table(['Volume name', 'capacity', 'Host Name', 'Location', 'Notes'],
                                 title="File Storage Details")
    for nas in nas_storage_data:
        table_nas.add_row([nas['username'], nas['capacityGb'],
                           nas['serviceResourceBackendIpAddress'],
                           nas['allowedHardware'][0]['datacenter']['longName'],
                           nas.get('notes', None)])

    table_hard_drives = formatting.Table(['Type', 'Name', 'Capacity', 'Serial #'], title="Other storage details")
    for drives in hard_drives:
        type_drive = drives['hardwareComponentModel']['hardwareGenericComponentModel']['hardwareComponentType']['type']
        name = drives['hardwareComponentModel']['manufacturer'] + " " + drives['hardwareComponentModel']['name']
        capacity = str(drives['hardwareComponentModel']['hardwareGenericComponentModel']['capacity']) + " " + str(
            drives['hardwareComponentModel']['hardwareGenericComponentModel']['units'])
        serial = drives['serialNumber']

        table_hard_drives.add_row([type_drive, name, capacity, serial])

    env.fout(table_credentials)
    env.fout(table_iscsi)
    env.fout(table_nas)
    env.fout(table_hard_drives)
