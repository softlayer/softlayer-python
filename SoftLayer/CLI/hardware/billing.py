"""Get billing for a hardware device."""
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
    """Get billing for a hardware device."""
    hardware = SoftLayer.HardwareManager(env.client)

    hardware_id = helpers.resolve_id(hardware.resolve_ids, identifier, 'hardware')
    result = hardware.get_hardware(hardware_id)
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['Id', identifier])

    table.add_row(['Billing Item Id', utils.lookup(result, 'billingItem', 'id')])
    table.add_row(['Recurring Fee', utils.lookup(result, 'billingItem', 'recurringFee')])
    table.add_row(['Total', utils.lookup(result, 'billingItem', 'nextInvoiceTotalRecurringAmount')])
    table.add_row(['Provision Date', utils.lookup(result, 'billingItem', 'provisionDate')])

    price_table = formatting.Table(['Item', 'Recurring Price'])
    for item in utils.lookup(result, 'billingItem', 'nextInvoiceChildren') or []:
        price_table.add_row([item['description'], item['nextInvoiceTotalRecurringAmount']])

    table.add_row(['prices', price_table])
    env.fout(table)
