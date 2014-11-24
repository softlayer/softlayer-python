"""List billing summary of Account."""
# :license: MIT, see LICENSE for more details.


import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

import click


@click.command()
@environment.pass_env
def cli(env):
    """List billing details of Account."""
    billing = SoftLayer.BillingManager(env.client)
    table = formatting.Table(['Name', 'Value'])
    balance = billing.get_balance()
    next_balance = billing.get_next_balance()
    table.add_row(['Current Balance', balance])
    table.add_row(['Estimated Next Balance', next_balance])
    return table
