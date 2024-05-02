"""Cancel an existing file storage volume."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume-id')
@click.option('--reason', help="An optional reason for cancellation")
@click.option('--immediate', is_flag=True,
              help="Cancels the file storage volume immediately instead of on the billing anniversary")
@click.option('--force', default=False, is_flag=True, help="Force modify")
@environment.pass_env
def cli(env, volume_id, reason, immediate, force):
    """Cancel an existing file storage volume.

    EXAMPLE::
        slcli file volume-cancel 12345678 --immediate -f
        This command cancels volume with ID 12345678 immediately and without asking for confirmation.
    """

    file_storage_manager = SoftLayer.FileStorageManager(env.client)

    if not force:
        if not (env.skip_confirmations or formatting.no_going_back(volume_id)):
            raise exceptions.CLIAbort('Aborted.')

    cancelled = file_storage_manager.cancel_file_volume(volume_id, reason, immediate)

    if cancelled:
        if immediate:
            click.echo(f'File volume with id {volume_id} has been marked for immediate cancellation')
        else:
            click.echo(f'File volume with id {volume_id} has been marked for cancellation')
    else:
        click.echo(f'Unable to cancle file volume {volume_id}')
