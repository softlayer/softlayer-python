"""List billing summary."""
# :license: MIT, see LICENSE for more details.


import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

import click


@click.command()
@environment.pass_env
def cli(env):
    """List billing summary."""
    billing = SoftLayer.BillingManager(env.client)
    table = formatting.Table(['Name', 'Value'])
    balance = billing.get_balance()
    next_balance = billing.get_next_balance()
    last_bill_date = billing.get_latest_bill_date()
    table.add_row(['Current Balance', balance])
    table.add_row(['Estimated Next Balance', next_balance])
    table.add_row(['Last Billing Date', last_bill_date])
    return table
