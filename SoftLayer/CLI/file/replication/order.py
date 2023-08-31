"""Order a file storage replica volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


CONTEXT_SETTINGS = {'token_normalize_func': lambda x: x.upper()}


@click.command(cls=SoftLayer.CLI.command.SLCommand, context_settings=CONTEXT_SETTINGS)
@click.argument('volume_id')
@click.option('--snapshot-schedule', '-s',
              help='Snapshot schedule to use for replication, '
              '(HOURLY | DAILY | WEEKLY)',
              required=True,
              type=click.Choice(['HOURLY', 'DAILY', 'WEEKLY']))
@click.option('--location', '-l',
              help='Short name of the data center for the replicant '
              '(e.g.: dal09)',
              required=True)
@click.option('--tier',
              help='Endurance Storage Tier (IOPS per GB) of the primary'
              ' volume for which a replicant is ordered [optional]',
              type=click.Choice(['0.25', '2', '4', '10']))
@click.option('--iops', '-i', type=int,
              help='Performance Storage IOPs, between 100 and 6000 in multiples of 100,'
              'if no IOPS value is specified, the IOPS value of the original volume will be used',
              )
@click.option('--force', default=False, is_flag=True, help="Force cancel block volume without confirmation")
@environment.pass_env
def cli(env, volume_id, snapshot_schedule, location, tier, iops, force):
    """Order a file storage replica volume.

    Example::
        slcli file replica-order 12345678 -s DAILY -d dal09 --tier 4 --os-type LINUX
        This command orders a replica for volume with ID 12345678, which performs DAILY
        replication, is located at dal09, tier level is 4, OS type is Linux.
    """
    file_manager = SoftLayer.FileStorageManager(env.client)
    file_volume_id = helpers.resolve_id(file_manager.resolve_ids, volume_id, 'File Storage')

    if tier is not None:
        tier = float(tier)

    if iops is not None:
        if iops < 100 or iops > 6000:
            raise exceptions.CLIHalt("-i|--iops must be between 100 and 6000, inclusive. "
                                     "Run 'slcli block volume-options' to check available options.")

        if iops % 100 != 0:
            raise exceptions.CLIHalt("-i|--iops must be a multiple of 100. "
                                     "Run 'slcli block volume-options' to check available options.")

    if not force:
        if not (env.skip_confirmations or
                formatting.confirm(f"This will Order a file storage replica volume: {volume_id} "
                                   "and cannot be undone. Continue?")):
            raise exceptions.CLIAbort('Aborted.')

    try:
        order = file_manager.order_replicant_volume(
            file_volume_id,
            snapshot_schedule=snapshot_schedule,
            location=location,
            tier=tier, iops=iops,
        )
    except ValueError as ex:
        raise exceptions.ArgumentError(str(ex))

    if 'placedOrder' in order.keys():
        click.echo(f"Order #{utils.lookup(order, 'placedOrder', 'id')} placed successfully!")
        for item in utils.lookup(order, 'placedOrder', 'items'):
            click.echo(" > %s" % item.get('description'))
    else:
        click.echo("Order could not be placed! Please verify your options " +
                   "and try again.")
