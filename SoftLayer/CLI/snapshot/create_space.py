"""Orders snapshot space for given iSCSI."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--capacity',
              type=click.INT,
              help="Size of snapshot space to create")
@environment.pass_env
def cli(env, identifier, capacity):
    """Orders snapshot space for given iSCSI."""

    iscsi_mgr = SoftLayer.ISCSIManager(env.client)
    iscsi_id = helpers.resolve_id(iscsi_mgr.resolve_ids, identifier, 'iSCSI')
    iscsi_mgr.create_snapshot_space(iscsi_id, capacity)
