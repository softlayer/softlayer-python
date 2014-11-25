"""Server order options for a given chassis."""
# :license: MIT, see LICENSE for more details.
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import hardware

import click


@click.command()
@environment.pass_env
def cli(env):
    """Server order options for a given chassis."""

    mask = """
id,
activePresets,
items[
    keyName,
    capacity,
    description,
    attributes[id,attributeTypeKeyName],
    softwareDescription[id,referenceCode,longDescription],
    itemCategory[id,categoryCode],
    prices
],
regions[location[location]]
"""
    package = env.client['Product_Package'].getObject(id=200, mask=mask)

    tables = []

    # Datacenters
    dc_table = formatting.Table(['datacenter', 'value'])
    for region in package['regions']:

        dc_table.add_row([region['location']['location']['longName'],
                          region['location']['location']['name'],
                          ])
    tables.append(dc_table)

    # Presets
    preset_table = formatting.Table(['size', 'value'])
    for preset in package['activePresets']:
        preset_table.add_row([preset['description'], preset['keyName']])
    tables.append(preset_table)

    # Operating systems
    os_table = formatting.Table(['operating_system', 'value'])
    for item in package['items']:
        if item['itemCategory']['categoryCode'] == 'os':
            os_table.add_row([item['softwareDescription']['longDescription'],
                              item['softwareDescription']['referenceCode']])
    tables.append(os_table)

    # Port speed
    port_speed_table = formatting.Table(['port_speed', 'value'])
    for item in package['items']:
        if all([item['itemCategory']['categoryCode'] == 'port_speed',
                not hardware.is_private_port_speed_item(item),
                ]):
            port_speed_table.add_row([item['description'], item['capacity']])
    tables.append(port_speed_table)

    port_speed_table = formatting.Table(['extras', 'value'])
    for item in package['items']:
        if item['itemCategory']['categoryCode'] in ['pri_ipv6_addresses',
                                                    'static_ipv6_addresses',
                                                    'sec_ip_addresses']:
            port_speed_table.add_row([item['description'], item['keyName']])
    tables.append(port_speed_table)
    return tables
