"""Remove resource record."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@click.argument('record_id')
@environment.pass_env
def cli(env, record_id):
    """Remove resource record."""

    manager = SoftLayer.DNSManager(env.client)

    if not (env.skip_confirmations or formatting.no_going_back('yes')):
        raise exceptions.CLIAbort("Aborted.")

    manager.delete_record(record_id)
