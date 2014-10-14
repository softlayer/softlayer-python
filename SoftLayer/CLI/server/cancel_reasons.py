"""Display a list of cancellation reasons"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Display a list of cancellation reasons"""

    table = formatting.Table(['Code', 'Reason'])
    table.align['Code'] = 'r'
    table.align['Reason'] = 'l'

    mgr = SoftLayer.HardwareManager(env.client)

    for code, reason in mgr.get_cancellation_reasons().items():
        table.add_row([code, reason])

    return table
