"""Virtual server order options."""
# :license: MIT, see LICENSE for more details.
# pylint: disable=too-many-statements
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(short_help="Get options to use for creating virtual servers.")
@click.option('--vsi-type', required=False, show_default=True, default='PUBLIC_CLOUD_SERVER',
              type=click.Choice(['TRANSIENT_CLOUD_SERVER', 'SUSPEND_CLOUD_SERVER', 'PUBLIC_CLOUD_SERVER']),
              help="Display options for a specific virtual server packages, for default is PUBLIC_CLOUD_SERVER, "
                   "choose between TRANSIENT_CLOUD_SERVER, SUSPEND_CLOUD_SERVER, PUBLIC_CLOUD_SERVER")
@environment.pass_env
def cli(env, vsi_type):
    """Virtual server order options."""

    vsi = SoftLayer.VSManager(env.client)
    options = vsi.get_create_options(vsi_type)

    tables = []

    # Datacenters
    dc_table = formatting.Table(['datacenter', 'Value'], title="Datacenters")
    dc_table.sortby = 'Value'
    dc_table.align = 'l'

    for location in options['locations']:
        dc_table.add_row([location['name'], location['key']])
    tables.append(dc_table)

    # Operation system
    os_table = formatting.Table(['OS', 'Key', 'Reference Code'], title="Operating Systems")
    os_table.sortby = 'Key'
    os_table.align = 'l'

    for operating_system in options['operating_systems']:
        os_table.add_row([operating_system['name'], operating_system['key'], operating_system['referenceCode']])
    tables.append(os_table)

    # Sizes
    preset_table = formatting.Table(['Size', 'Value'], title="Sizes")
    preset_table.sortby = 'Value'
    preset_table.align = 'l'

    for size in options['sizes']:
        preset_table.add_row([size['name'], size['key']])
    tables.append(preset_table)

    #  RAM
    ram_table = formatting.Table(['memory', 'Value'], title="RAM")
    ram_table.sortby = 'Value'
    ram_table.align = 'l'

    for ram in options['ram']:
        ram_table.add_row([ram['name'], ram['key']])
    tables.append(ram_table)

    # Data base
    database_table = formatting.Table(['database', 'Value'], title="Databases")
    database_table.sortby = 'Value'
    database_table.align = 'l'

    for database in options['database']:
        database_table.add_row([database['name'], database['key']])
    tables.append(database_table)

    # Guest_core
    guest_core_table = formatting.Table(['cpu', 'Value', 'Capacity'], title="Guest_core")
    guest_core_table.sortby = 'Value'
    guest_core_table.align = 'l'

    for guest_core in options['guest_core']:
        guest_core_table.add_row([guest_core['name'], guest_core['key'], guest_core['capacity']])
    tables.append(guest_core_table)

    # Guest_core
    guest_disk_table = formatting.Table(['guest_disk', 'Value', 'Capacity', 'Disk'], title="Guest_disks")
    guest_disk_table.sortby = 'Value'
    guest_disk_table.align = 'l'

    for guest_disk in options['guest_disk']:
        guest_disk_table.add_row([guest_disk['name'], guest_disk['key'], guest_disk['capacity'], guest_disk['disk']])
    tables.append(guest_disk_table)

    # Port speed
    port_speed_table = formatting.Table(['network', 'Key'], title="Network Options")
    port_speed_table.sortby = 'Key'
    port_speed_table.align = 'l'

    for speed in options['port_speed']:
        port_speed_table.add_row([speed['name'], speed['key']])
    tables.append(port_speed_table)

    env.fout(formatting.listing(tables, separator='\n'))
