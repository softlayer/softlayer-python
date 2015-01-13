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
    result = billing.get_summary()
    balance = result['balance']
    next_balance = result['nextbalance']
    last_bill_date = result['lastbilldate']
    table.add_row(['Current Balance', balance])
    table.add_row(['Estimated Next Balance', next_balance])
    table.add_row(['Last Billing Date', last_bill_date])
    return table
