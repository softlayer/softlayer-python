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
    dc_table = formatting.Table(['datacenter', 'value'])
    dc_table.sortby = 'value'
    for location in options['locations']:
        dc_table.add_row([location['name'], location['key']])
    tables.append(dc_table)

    # Presets
    preset_table = formatting.Table(['size', 'value'])
    preset_table.sortby = 'value'
    for size in options['sizes']:
        preset_table.add_row([size['name'], size['key']])
    tables.append(preset_table)

    # Operating systems
    os_table = formatting.Table(['operating_system', 'value'])
    os_table.sortby = 'value'
    for operating_system in options['operating_systems']:
        os_table.add_row([operating_system['name'], operating_system['key']])
    tables.append(os_table)

    # Port speed
    port_speed_table = formatting.Table(['port_speed', 'value'])
    port_speed_table.sortby = 'value'
    for speed in options['port_speeds']:
        port_speed_table.add_row([speed['name'], speed['key']])
    tables.append(port_speed_table)

    # Extras
    extras_table = formatting.Table(['extras', 'value'])
    extras_table.sortby = 'value'
    for extra in options['extras']:
        extras_table.add_row([extra['name'], extra['key']])
    tables.append(extras_table)

    env.fout(formatting.listing(tables, separator='\n'))
