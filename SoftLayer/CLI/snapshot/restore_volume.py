"""Restores volume from existing snapshot."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('snapshot-id')
@click.argument('volume-id')
@environment.pass_env
def cli(env, snapshot_id, volume_id):
    """Restores volume from existing snapshot."""
    iscsi_mgr = SoftLayer.ISCSIManager(env.client)
    volume_id = helpers.resolve_id(iscsi_mgr.resolve_ids, volume_id, 'iSCSI')
    snapshot_id = helpers.resolve_id(iscsi_mgr.resolve_ids,
                                     snapshot_id,
                                     'Snapshot')
    iscsi_mgr.restore_from_snapshot(volume_id, snapshot_id)
