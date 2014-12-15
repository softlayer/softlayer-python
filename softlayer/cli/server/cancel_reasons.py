"""Display a list of cancellation reasons."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting

import click


@click.command()
@environment.pass_env
def cli(env):
    """Display a list of cancellation reasons."""

    table = formatting.Table(['Code', 'Reason'])
    table.align['Code'] = 'r'
    table.align['Reason'] = 'l'

    mgr = softlayer.HardwareManager(env.client)

    for code, reason in mgr.get_cancellation_reasons().items():
        table.add_row([code, reason])

    return table
