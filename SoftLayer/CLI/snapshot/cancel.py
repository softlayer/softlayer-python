"""Cancel/Delete iSCSI snapshot."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel/Delete iSCSI snapshot."""

    iscsi_mgr = SoftLayer.ISCSIManager(env.client)
    snapshot_id = helpers.resolve_id(iscsi_mgr.resolve_ids,
                                     identifier,
                                     'Snapshot')
    iscsi_mgr.delete_snapshot(snapshot_id)
