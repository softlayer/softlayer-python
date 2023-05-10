"""Displays information about the accounts bandwidth pools"""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils


@click.command(cls=SLCommand, )
@environment.pass_env
def cli(env):
    """Displays bandwidth pool information

    Similiar to https://cloud.ibm.com/classic-bandwidth/pools
    """

    manager = AccountManager(env.client)
    items = manager.get_bandwidth_pools()

    table = formatting.Table([
        "Id",
        "Name",
        "Region",
        "Devices",
        "Allocation",
        "Current Usage",
        "Projected Usage",
        "Cost"
    ], title="Bandwidth Pools")
    table.align = 'l'
    for item in items:
        id_bandwidth = item.get('id')
        name = item.get('name')
        region = utils.lookup(item, 'locationGroup', 'name')
        servers = manager.get_bandwidth_pool_counts(identifier=item.get('id'))
        allocation = "{} GB".format(item.get('totalBandwidthAllocated', 0))

        current = utils.lookup(item, 'billingCyclePublicBandwidthUsage', 'amountOut')
        if current is not None:
            current = "{} GB".format(current)
        else:
            current = "0 GB"

        projected = "{} GB".format(item.get('projectedPublicBandwidthUsage', 0))

        cost = utils.lookup(item, 'billingItem', 'nextInvoiceTotalRecurringAmount')
        if cost is not None:
            cost = "${}".format(cost)
        else:
            cost = "$0.0"

        table.add_row([id_bandwidth, name, region, servers, allocation, current, projected, cost])
    env.fout(table)
