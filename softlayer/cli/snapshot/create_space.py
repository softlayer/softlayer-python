"""Orders snapshot space for given iSCSI."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import helpers


import click


@click.command()
@click.argument('identifier')
@click.option('--capacity',
              type=click.INT,
              help="Size of snapshot space to create")
@environment.pass_env
def cli(env, identifier, capacity):
    """Orders snapshot space for given iSCSI."""

    iscsi_mgr = softlayer.ISCSIManager(env.client)
    iscsi_id = helpers.resolve_id(iscsi_mgr.resolve_ids, identifier, 'iSCSI')
    iscsi_mgr.create_snapshot_space(iscsi_id, capacity)
