"""List Reserved Capacity"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager


@click.command()
@environment.pass_env
def cli(env):
    """List Reserved Capacity groups."""
    manager = CapacityManager(env.client)
    result = manager.list()
    table = formatting.Table(
        ["ID", "Name", "Capacity", "Flavor", "Location",  "Created"], 
        title="Reserved Capacity"
    )
    for rc in result:
        occupied_string = "#" * int(rc.get('occupiedInstanceCount',0))
        available_string = "-" * int(rc.get('availableInstanceCount',0))

        try:
            flavor = rc['instances'][0]['billingItem']['description']
            cost = float(rc['instances'][0]['billingItem']['hourlyRecurringFee'])
        except KeyError:
            flavor = "Unknown Billing Item"
        location = rc['backendRouter']['hostname']
        capacity = "%s%s" % (occupied_string, available_string)
        table.add_row([rc['id'], rc['name'], capacity, flavor, location, rc['createDate']])
    env.fout(table)
