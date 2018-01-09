"""Get details for a dedicated host."""
# :license: MIT, see LICENSE for more details.

import logging

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

LOGGER = logging.getLogger(__name__)


@click.command()
@click.argument('identifier')
@click.option('--price', is_flag=True, help='Show associated prices')
@click.option('--guests', is_flag=True, help='Show guests on dedicated host')
@environment.pass_env
def cli(env, identifier, price=False, guests=False):
    """Get details for a virtual server."""
    dhost = SoftLayer.DedicatedHostManager(env.client)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    result = dhost.get_host(identifier)
    result = utils.NestedDict(result)

    table.add_row(['id', result['id']])
    table.add_row(['name', result['name']])
    table.add_row(['cpu count', result['cpuCount']])
    table.add_row(['memory capacity', result['memoryCapacity']])
    table.add_row(['disk capacity', result['diskCapacity']])
    table.add_row(['create date', result['createDate']])
    table.add_row(['modify date', result['modifyDate']])
    table.add_row(['router id', result['backendRouter']['id']])
    table.add_row(['router hostname', result['backendRouter']['hostname']])
    table.add_row(['owner', formatting.FormattedItem(
        utils.lookup(result, 'billingItem', 'orderItem', 'order', 'userRecord', 'username') or formatting.blank(),)])

    if price:
        total_price = utils.lookup(result,
                                   'billingItem',
                                   'nextInvoiceTotalRecurringAmount') or 0
        total_price += sum(p['nextInvoiceTotalRecurringAmount']
                           for p
                           in utils.lookup(result,
                                           'billingItem',
                                           'children') or [])
        table.add_row(['price_rate', total_price])

    table.add_row(['guest count', result['guestCount']])
    if guests:
        guest_table = formatting.Table(['id', 'hostname', 'domain', 'uuid'])
        for guest in result['guests']:
            guest_table.add_row([
                guest['id'], guest['hostname'], guest['domain'], guest['uuid']])
        table.add_row(['guests', guest_table])

    table.add_row(['datacenter', result['datacenter']['name']])

    env.fout(table)
