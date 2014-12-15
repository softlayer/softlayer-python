"""Cancel an existing iSCSI account."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting
from softlayer.cli import helpers

import click


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

    iscsi_mgr = softlayer.ISCSIManager(env.client)
    iscsi_id = helpers.resolve_id(iscsi_mgr.resolve_ids, identifier, 'iSCSI')

    if env.skip_confirmations or formatting.no_going_back(iscsi_id):
        iscsi_mgr.cancel_iscsi(iscsi_id, reason, immediate)
    else:
        raise exceptions.CLIAbort('Aborted')
