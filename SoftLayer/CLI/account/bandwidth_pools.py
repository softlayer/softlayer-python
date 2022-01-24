"""Displays information about the accounts bandwidth pools"""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils

from pprint import pprint as pp

@click.command()
@environment.pass_env
def cli(env):
    """Lists billing items with some other useful information.

    Similiar to https://cloud.ibm.com/billing/billing-items
    """

    manager = AccountManager(env.client)
    items = manager.get_bandwidth_pools()
    # table = item_table(items)
    pp(items)
    table = formatting.Table([
        "Pool Name",
        "Region",
        "Servers",
        "Allocation",
        "Current Usage",
        "Projected Usage"
    ], title="Bandwidth Pools")
    table.align = 'l'

    for item in items:
        name = item.get('name')
        region = utils.lookup(item, 'locationGroup', 'name')
        servers = manager.get_bandwidth_pool_counts(identifier=item.get('id'))
        allocation = item.get('totalBandwidthAllocated', 0)
        current = item.get('billingCyclePublicUsageTotal', 0)
        projected = item.get('projectedPublicBandwidthUsage', 0)

        table.add_row([name, region, servers, allocation, current, projected,])
    env.fout(table)
