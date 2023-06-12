"""Order snapshot space for a block storage volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume_id')
@click.option('--iops',
              type=int,
              help='Performance Storage IOPs, between 100 and 6000 in multiples of 100.')
@click.option('--size',
              type=int,
              help='Size of snapshot space to create in GB.',
              required=True)
@click.option('--tier',
              help='Endurance Storage Tier (IOPS per GB) of the block'
              ' volume for which space is ordered [optional, and only'
              ' valid for endurance storage volumes].',
              type=click.Choice(['0.25', '2', '4', '10']))
@click.option('--upgrade',
              type=bool,
              help='Flag to indicate that the order is an upgrade.',
              default=False,
              is_flag=True)
@environment.pass_env
def cli(env, volume_id, size, tier, upgrade, iops):
    """Order snapshot space for a block storage volume."""
    block_manager = SoftLayer.BlockStorageManager(env.client)

    if tier is not None:
        tier = float(tier)

    if iops is not None:
        if iops < 100 or iops > 6000:
            raise exceptions.ArgumentError(f"Invalid value for '--iops' / '-i': '{iops}' is not one "
                                           "of between 100 and 6000.")
        if iops % 100 != 0:
            raise exceptions.ArgumentError(f"Invalid value for '--iops' / '-i': '{iops}' is not a multiple of 100.")

    try:
        order = block_manager.order_snapshot_space(
            volume_id,
            capacity=size,
            tier=tier,
            upgrade=upgrade,
            iops=iops
        )
    except ValueError as ex:
        raise exceptions.ArgumentError(str(ex))

    if 'placedOrder' in order.keys():
        click.echo(f"Order #{order['placedOrder']['id']} placed successfully!")
        for item in order['placedOrder']['items']:
            click.echo(" > %s" % item['description'])
        if 'status' in order['placedOrder'].keys():
            click.echo(" > Order status: %s" % order['placedOrder']['status'])
    else:
        click.echo("Order could not be placed! Please verify your options " +
                   "and try again.")
