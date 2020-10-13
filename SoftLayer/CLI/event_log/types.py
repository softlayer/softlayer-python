"""Get Event Log Types."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

COLUMNS = ['types']


@click.command()
@environment.pass_env
def cli(env):
    """Get Event Log Types"""
    mgr = SoftLayer.EventLogManager(env.client)

    event_log_types = mgr.get_event_log_types()

    table = formatting.Table(COLUMNS)

    for event_log_type in event_log_types:
        table.add_row([event_log_type])

    env.fout(table)
