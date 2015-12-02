"""Display a list of cancellation reasons."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """Display a list of cancellation reasons."""

    table = formatting.Table(['Code', 'Reason'])
    table.align['Code'] = 'r'
    table.align['Reason'] = 'l'

    mgr = SoftLayer.HardwareManager(env.client)

    for code, reason in mgr.get_cancellation_reasons().items():
        table.add_row([code, reason])

    env.fout(table)
