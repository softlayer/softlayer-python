"""Update firmware."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Update server firmware."""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')
    if not (env.skip_confirmations or
            formatting.confirm('This will power off the server with id %s and '
                               'update device firmware. Continue?' % hw_id)):
        raise exceptions.CLIAbort('Aborted.')

    mgr.update_firmware(hw_id)
