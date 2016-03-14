"""Cancel a dedicated server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--immediate',
              is_flag=True,
              default=False,
              help="""Cancels the server immediately (instead of on the billing
 anniversary)""")
@click.option('--comment',
              help="An optional comment to add to the cancellation ticket")
@click.option('--reason',
              help="""An optional cancellation reason. See cancel-reasons for
 a list of available options""")
@environment.pass_env
def cli(env, identifier, immediate, comment, reason):
    """Cancel a dedicated server."""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')

    if not (env.skip_confirmations or formatting.no_going_back(hw_id)):
        raise exceptions.CLIAbort('Aborted')

    mgr.cancel_hardware(hw_id, reason, comment, immediate)
