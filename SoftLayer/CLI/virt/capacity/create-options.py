"""List options for creating Reserved Capacity"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager


from pprint import pprint as pp

@click.command()
@environment.pass_env
def cli(env):
    """List options for creating Reserved Capacity"""
    manager = CapacityManager(env.client)
    items = manager.get_create_options()
    items.sort(key=lambda term: int(term['capacity']))
    table = formatting.Table(["KeyName", "Description", "Term", "Hourly Price"], title="Reserved Capacity Options")
    table.align["Hourly Price"] = "l"
    table.align["Description"] = "l"
    table.align["KeyName"] = "l"
    for item in items:
        table.add_row([
            item['keyName'], item['description'], item['capacity'], get_price(item)
        ])
    # pp(items)
    env.fout(table)


def get_price(item):
    the_price = "No Default Pricing"
    for price in item.get('prices',[]):
        if price.get('locationGroupId') == '':
            the_price = "%0.4f"  % float(price['hourlyRecurringFee'])
    return the_price


