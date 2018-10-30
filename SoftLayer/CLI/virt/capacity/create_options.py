"""List options for creating Reserved Capacity"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager


@click.command()
@environment.pass_env
def cli(env):
    """List options for creating Reserved Capacity"""
    manager = CapacityManager(env.client)
    items = manager.get_create_options()

    items.sort(key=lambda term: int(term['capacity']))
    table = formatting.Table(["KeyName", "Description", "Term", "Default Hourly Price Per Instance"],
                             title="Reserved Capacity Options")
    table.align["Hourly Price"] = "l"
    table.align["Description"] = "l"
    table.align["KeyName"] = "l"
    for item in items:
        table.add_row([
            item['keyName'], item['description'], item['capacity'], get_price(item)
        ])
    env.fout(table)

    regions = manager.get_available_routers()
    location_table = formatting.Table(['Location', 'POD', 'BackendRouterId'], 'Orderable Locations')
    for region in regions:
        for location in region['locations']:
            for pod in location['location']['pods']:
                location_table.add_row([region['keyname'], pod['backendRouterName'], pod['backendRouterId']])
    env.fout(location_table)


def get_price(item):
    """Finds the price with the default locationGroupId"""
    the_price = "No Default Pricing"
    for price in item.get('prices', []):
        if not price.get('locationGroupId'):
            the_price = "%0.4f" % float(price['hourlyRecurringFee'])
    return the_price
