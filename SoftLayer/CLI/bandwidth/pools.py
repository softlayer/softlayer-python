"""Displays information about the bandwidth pools"""
# :license: MIT, see LICENSE for more details.
import concurrent.futures as cf
import logging
import time

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils

LOGGER = logging.getLogger(__name__)


@click.command(cls=SLCommand, )
@environment.pass_env
def cli(env):
    """Displays bandwidth pool information

    Similiar to https://cloud.ibm.com/classic-bandwidth/pools

    More information
    https://cloud.ibm.com/docs/bandwidth-metering?topic=bandwidth-metering-get-started-with-bandwidth-metering
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
        "Cost",
        "Deletion"
    ], title="Bandwidth Pools")
    table.align = 'l'

    start_m = time.perf_counter()

    with cf.ThreadPoolExecutor(max_workers=5) as executor:
        for item, servers in zip(items, executor.map(manager.get_bandwidth_pool_counts,
                                                     [item.get('id') for item in items])):

            id_bandwidth = item.get('id')
            name = item.get('name')
            region = utils.lookup(item, 'locationGroup', 'name')

            allocation = f"{item.get('totalBandwidthAllocated', 0)} GB"

            current = utils.lookup(item, 'billingCyclePublicBandwidthUsage', 'amountOut')
            if current is not None:
                current = f"{current} GB"
            else:
                current = "0 GB"

            projected = f"{item.get('projectedPublicBandwidthUsage', 0)} GB"

            cost = utils.lookup(item, 'billingItem', 'nextInvoiceTotalRecurringAmount')
            if cost is not None:
                cost = f"${cost}"
            else:
                cost = "$0.0"

            deletion = utils.clean_time(item.get('endDate'))
            if deletion == '':
                deletion = formatting.blank()

            table.add_row([id_bandwidth, name, region, servers, allocation, current, projected, cost, deletion])

    end_m = time.perf_counter()
    LOGGER.debug('Total API Call time %s', end_m - start_m)
    env.fout(table)
