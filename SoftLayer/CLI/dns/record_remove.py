"""Remove resource record."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('record_id')
@environment.pass_env
def cli(env, record_id):
    """Remove resource record.

    Example::
        slcli dns record-remove 12345678
        This command removes resource record with ID 12345678.
"""

    manager = SoftLayer.DNSManager(env.client)

    if not (env.skip_confirmations or formatting.no_going_back('yes')):
        raise exceptions.CLIAbort("Aborted.")

    manager.delete_record(record_id)
