"""Server order options for a given chassis."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import hardware


@click.command()
@environment.pass_env
def cli(env):
    """Server order options for a given chassis."""

    hardware_manager = hardware.HardwareManager(env.client)
    options = hardware_manager.get_create_options()

    tables = []

    # Datacenters
    dc_table = formatting.Table(['Datacenter', 'Value'], title="Datacenters")
    dc_table.sortby = 'Value'
    dc_table.align = 'l'
    for location in options['locations']:
        dc_table.add_row([location['name'], location['key']])
    tables.append(dc_table)

    # Presets
    preset_table = formatting.Table(['Size', 'Value'], title="Sizes")
    preset_table.sortby = 'Value'
    preset_table.align = 'l'
    for size in options['sizes']:
        preset_table.add_row([size['name'], size['key']])
    tables.append(preset_table)

    # Operating systems
    os_table = formatting.Table(['OS', 'Key', 'Reference Code'], title="Operating Systems")
    os_table.sortby = 'Key'
    os_table.align = 'l'
    for operating_system in options['operating_systems']:
        os_table.add_row([operating_system['name'], operating_system['key'], operating_system['referenceCode']])
    tables.append(os_table)

    # Port speed
    port_speed_table = formatting.Table(['Network', 'Speed', 'Key'], title="Network Options")
    port_speed_table.sortby = 'Speed'
    port_speed_table.align = 'l'

    for speed in options['port_speeds']:
        port_speed_table.add_row([speed['name'], speed['speed'], speed['key']])
    tables.append(port_speed_table)

    # Extras
    extras_table = formatting.Table(['Extra Option', 'Value'], title="Extras")
    extras_table.sortby = 'Value'
    extras_table.align = 'l'
    for extra in options['extras']:
        extras_table.add_row([extra['name'], extra['key']])
    tables.append(extras_table)

    env.fout(formatting.listing(tables, separator='\n'))
