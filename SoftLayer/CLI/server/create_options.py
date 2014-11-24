"""Server order options for a given chassis."""
# :license: MIT, see LICENSE for more details.
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

import click


@click.command()
@environment.pass_env
def cli(env):
    """Server order options for a given chassis."""

    mask = """
id,
activePresets,
items[keyName,description,itemCategory[id,categoryCode]],
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
            os_table.add_row([item['description'], item['keyName']])
    tables.append(os_table)

    return tables
