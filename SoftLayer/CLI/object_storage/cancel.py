"""Cancel an existing object-storage account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('storage-id')
@click.option('--reason', help="An optional reason for cancellation")
@click.option('--immediate',
              is_flag=True,
              help="Cancels the object storage immediately instead "
                   "of on the billing anniversary")
@environment.pass_env
def cli(env, storage_id, reason, immediate):
    """Cancel an existing object storage."""

    block_storage_manager = SoftLayer.BlockStorageManager(env.client)

    if not (env.skip_confirmations or formatting.no_going_back(storage_id)):
        raise exceptions.CLIAbort('Aborted')

    cancelled = block_storage_manager.cancel_block_volume(storage_id,
                                                          reason, immediate)

    if cancelled:
        if immediate:
            click.echo('Object storage with id %s has been marked'
                       ' for immediate cancellation' % storage_id)
        else:
            click.echo('Object storage with id %s has been marked'
                       ' for cancellation' % storage_id)
    else:
        click.echo('Unable to cancel object storage %s' % storage_id)
