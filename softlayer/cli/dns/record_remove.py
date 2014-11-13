"""Remove resource record."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting

import click


@click.command()
@click.argument('record_id')
@environment.pass_env
def cli(env, record_id):
    """Add resource record."""

    manager = softlayer.DNSManager(env.client)

    if env.skip_confirmations or formatting.no_going_back('yes'):
        manager.delete_record(record_id)
    else:
        raise exceptions.CLIAbort("Aborted.")
