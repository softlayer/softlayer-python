"""List Reserved Capacity"""

import click

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
        ["ID", "Name", "Capacity", "Flavor", "Location", "Created"],
        title="Reserved Capacity"
    )
    for r_c in result:
        occupied_string = "#" * int(r_c.get('occupiedInstanceCount', 0))
        available_string = "-" * int(r_c.get('availableInstanceCount', 0))

        try:
            flavor = r_c['instances'][0]['billingItem']['description']
            # cost = float(r_c['instances'][0]['billingItem']['hourlyRecurringFee'])
        except KeyError:
            flavor = "Unknown Billing Item"
        location = r_c['backendRouter']['hostname']
        capacity = "%s%s" % (occupied_string, available_string)
        table.add_row([r_c['id'], r_c['name'], capacity, flavor, location, r_c['createDate']])
    env.fout(table)
