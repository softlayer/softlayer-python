"""Order a file storage replica volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers
from SoftLayer import utils


CONTEXT_SETTINGS = {'token_normalize_func': lambda x: x.upper()}


@click.command(context_settings=CONTEXT_SETTINGS)
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
@environment.pass_env
def cli(env, volume_id, snapshot_schedule, location, tier):
    """Order a file storage replica volume."""
    file_manager = SoftLayer.FileStorageManager(env.client)
    file_volume_id = helpers.resolve_id(file_manager.resolve_ids, volume_id, 'File Storage')

    if tier is not None:
        tier = float(tier)

    try:
        order = file_manager.order_replicant_volume(
            file_volume_id,
            snapshot_schedule=snapshot_schedule,
            location=location,
            tier=tier,
        )
    except ValueError as ex:
        raise exceptions.ArgumentError(str(ex))

    if 'placedOrder' in order.keys():
        click.echo("Order #{0} placed successfully!".format(
            utils.lookup(order, 'placedOrder', 'id')))
        for item in utils.lookup(order, 'placedOrder', 'items'):
            click.echo(" > %s" % item.get('description'))
    else:
        click.echo("Order could not be placed! Please verify your options " +
                   "and try again.")
