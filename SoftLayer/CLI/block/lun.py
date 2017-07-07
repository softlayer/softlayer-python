"""Set the LUN ID on an iSCSI volume."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('volume-id')
@click.argument('lun-id')
@environment.pass_env
def cli(env, volume_id, lun_id):
    """Set the LUN ID on an existing block storage volume.

    The LUN ID only takes effect during the Host Authorization process. It is
    recommended (but not necessary) to de-authorize all hosts before using this
    method. See `block access-revoke`.

    VOLUME_ID - the volume ID on which to set the LUN ID.

    LUN_ID - recommended range is an integer between 0 and 255. Advanced users
    can use an integer between 0 and 4095.
    """

    block_storage_manager = SoftLayer.BlockStorageManager(env.client)

    res = block_storage_manager.create_or_update_lun_id(volume_id, lun_id)

    if 'value' in res and lun_id == res['value']:
        click.echo(
            'Block volume with id %s is reporting LUN ID %s' % (res['volumeId'], res['value']))
    else:
        click.echo(
            'Failed to confirm the new LUN ID on volume %s' % (volume_id))
