"""Get billing for a virtual device."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get billing for a virtual device."""
    virtual = SoftLayer.VSManager(env.client)

    virtual_id = helpers.resolve_id(virtual.resolve_ids, identifier, 'virtual')
    result = virtual.get_instance(virtual_id)
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['Id', identifier])

    table.add_row(['Billing Item Id', utils.lookup(result, 'billingItem', 'id')])
    table.add_row(['Recurring Fee', utils.lookup(result, 'billingItem', 'recurringFee')])
    table.add_row(['Total', utils.lookup(result, 'billingItem', 'nextInvoiceTotalRecurringAmount')])
    table.add_row(['Provision Date', utils.lookup(result, 'billingItem', 'provisionDate')])

    price_table = formatting.Table(['Recurring Price'])
    for item in utils.lookup(result, 'billingItem', 'children') or []:
        price_table.add_row([item['nextInvoiceTotalRecurringAmount']])

    table.add_row(['prices', price_table])
    env.fout(table)
