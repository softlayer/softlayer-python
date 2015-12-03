"""Cancel an existing iSCSI account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--reason', help="An optional reason for cancellation")
@click.option('--immediate',
              is_flag=True,
              help="Cancels the iSCSI immediately instead of on the billing "
                   "anniversary")
@environment.pass_env
def cli(env, identifier, reason, immediate):
    """Cancel an existing iSCSI account."""

    iscsi_mgr = SoftLayer.ISCSIManager(env.client)
    iscsi_id = helpers.resolve_id(iscsi_mgr.resolve_ids, identifier, 'iSCSI')

    if not (env.skip_confirmations or formatting.no_going_back(iscsi_id)):
        raise exceptions.CLIAbort('Aborted')

    iscsi_mgr.cancel_iscsi(iscsi_id, reason, immediate)
