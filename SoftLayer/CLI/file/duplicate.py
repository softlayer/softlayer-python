"""Order a duplicate file storage volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


CONTEXT_SETTINGS = {'token_normalize_func': lambda x: x.upper()}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('origin-volume-id')
@click.option('--origin-snapshot-id', '-o',
              type=int,
              help="ID of an origin volume snapshot to use for duplcation.")
@click.option('--duplicate-size', '-c',
              type=int,
              help='Size of duplicate file volume in GB. '
                   '***If no size is specified, the size of '
                   'the origin volume will be used.***\n'
                   'Minimum: [the size of the origin volume]')
@click.option('--duplicate-iops', '-i',
              type=int,
              help='Performance Storage IOPS, between 100 and 6000 in '
                   'multiples of 100 [only used for performance volumes] '
                   '***If no IOPS value is specified, the IOPS value of the '
                   'origin volume will be used.***\n'
                   'Requirements: [If IOPS/GB for the origin volume is less '
                   'than 0.3, IOPS/GB for the duplicate must also be less '
                   'than 0.3. If IOPS/GB for the origin volume is greater '
                   'than or equal to 0.3, IOPS/GB for the duplicate must '
                   'also be greater than or equal to 0.3.]')
@click.option('--duplicate-tier', '-t',
              help='Endurance Storage Tier (IOPS per GB) [only used for '
                   'endurance volumes] ***If no tier is specified, the tier '
                   'of the origin volume will be used.***\n'
                   'Requirements: [If IOPS/GB for the origin volume is 0.25, '
                   'IOPS/GB for the duplicate must also be 0.25. If IOPS/GB '
                   'for the origin volume is greater than 0.25, IOPS/GB '
                   'for the duplicate must also be greater than 0.25.]',
              type=click.Choice(['0.25', '2', '4', '10']))
@click.option('--duplicate-snapshot-size', '-s',
              type=int,
              help='The size of snapshot space to order for the duplicate. '
                   '***If no snapshot space size is specified, the snapshot '
                   'space size of the origin file volume will be used.***\n'
                   'Input "0" for this parameter to order a duplicate volume '
                   'with no snapshot space.')
@click.option('--billing',
              type=click.Choice(['hourly', 'monthly']),
              default='monthly',
              help="Optional parameter for Billing rate (default to monthly)")
@environment.pass_env
def cli(env, origin_volume_id, origin_snapshot_id, duplicate_size,
        duplicate_iops, duplicate_tier, duplicate_snapshot_size, billing):
    """Order a duplicate file storage volume."""
    file_manager = SoftLayer.FileStorageManager(env.client)

    hourly_billing_flag = False
    if billing.lower() == "hourly":
        hourly_billing_flag = True

    if duplicate_tier is not None:
        duplicate_tier = float(duplicate_tier)

    try:
        order = file_manager.order_duplicate_volume(
            origin_volume_id,
            origin_snapshot_id=origin_snapshot_id,
            duplicate_size=duplicate_size,
            duplicate_iops=duplicate_iops,
            duplicate_tier_level=duplicate_tier,
            duplicate_snapshot_size=duplicate_snapshot_size,
            hourly_billing_flag=hourly_billing_flag
        )
    except ValueError as ex:
        raise exceptions.ArgumentError(str(ex))

    if 'placedOrder' in order.keys():
        click.echo("Order #{0} placed successfully!".format(
            order['placedOrder']['id']))
        for item in order['placedOrder']['items']:
            click.echo(" > %s" % item['description'])
    else:
        click.echo("Order could not be placed! Please verify your options " +
                   "and try again.")
