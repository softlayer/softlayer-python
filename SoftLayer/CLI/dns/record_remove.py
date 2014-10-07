"""Remove resource record"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting

import click


@click.command()
@click.argument('record_id')
@environment.pass_env
def cli(env, record_id):
    """Add resource record"""

    manager = SoftLayer.DNSManager(env.client)

    if env.skip_confirmations or formatting.no_going_back('yes'):
        manager.delete_record(record_id)
    raise exceptions.CLIAbort("Aborted.")
