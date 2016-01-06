"""Create a snapshot of an iSCSI volume."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--notes', help="An optional note for the snapshot")
@environment.pass_env
def cli(env, identifier, notes):
    """Create a snapshot of an iSCSI volume."""

    iscsi_mgr = SoftLayer.ISCSIManager(env.client)
    iscsi_id = helpers.resolve_id(iscsi_mgr.resolve_ids, identifier, 'iSCSI')
    iscsi_mgr.create_snapshot(iscsi_id, notes)
