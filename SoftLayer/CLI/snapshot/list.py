"""List iSCSI Snapshots."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


@click.command()
@click.argument('iscsi-identifier')
@environment.pass_env
def cli(env, iscsi_identifier):
    """List iSCSI Snapshots."""

    iscsi_mgr = SoftLayer.ISCSIManager(env.client)
    iscsi_id = helpers.resolve_id(iscsi_mgr.resolve_ids,
                                  iscsi_identifier,
                                  'iSCSI')
    iscsi = env.client['Network_Storage_Iscsi']
    snapshots = iscsi.getPartnerships(
        mask='volumeId,partnerVolumeId,createDate,type', id=iscsi_id)
    snapshots = [utils.NestedDict(n) for n in snapshots]

    table = formatting.Table(['id', 'createDate', 'name', 'description'])

    for snapshot in snapshots:
        table.add_row([
            snapshot['partnerVolumeId'],
            snapshot['createDate'],
            snapshot['type']['name'],
            snapshot['type']['description'],
        ])
    env.fout(table)
