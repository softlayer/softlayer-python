"""Cancel an existing iSCSI account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume-id')
@click.option('--reason', help="An optional reason for cancellation")
@click.option('--immediate',
              is_flag=True,
              help="Cancels the block storage volume immediately instead "
                   "of on the billing anniversary")
@click.option('--force', default=False, is_flag=True, help="Force cancel block volume without confirmation")
@environment.pass_env
def cli(env, volume_id, reason, immediate, force):
    """Cancel an existing block storage volume.

    Example::
        slcli block volume-cancel 12345678 --immediate -f
        This command cancels volume with ID 12345678 immediately and without asking for confirmation.
"""

    block_storage_manager = SoftLayer.BlockStorageManager(env.client)

    if not force:
        if not (env.skip_confirmations or
                formatting.confirm(f"This will cancel the block volume: {volume_id} and cannot be undone. Continue?")):
            raise exceptions.CLIAbort('Aborted')

    cancelled = block_storage_manager.cancel_block_volume(volume_id,
                                                          reason, immediate)

    if cancelled:
        if immediate:
            click.echo('Block volume with id %s has been marked'
                       ' for immediate cancellation' % volume_id)
        else:
            click.echo('Block volume with id %s has been marked'
                       ' for cancellation' % volume_id)
    else:
        click.echo('Unable to cancel block volume %s' % volume_id)
