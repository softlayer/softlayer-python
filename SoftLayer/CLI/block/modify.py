"""Modify an existing block storage volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer import utils


CONTEXT_SETTINGS = {'token_normalize_func': lambda x: x.upper()}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('volume-id')
@click.option('--new-size', '-c',
              type=int,
              help='New Size of block volume in GB. '
                   '***If no size is specified, the original size of '
                   'volume will be used.***\n'
                   'Potential Sizes: [20, 40, 80, 100, 250, '
                   '500, 1000, 2000, 4000, 8000, 12000] '
                   'Minimum: [the size of the origin volume] '
                   'Maximum: [the minimum of 12000 GB or '
                   '10*(origin volume size)]')
@click.option('--new-iops', '-i',
              type=int,
              help='Performance Storage IOPS, between 100 and 6000 in '
                   'multiples of 100 [only used for performance volumes] '
                   '***If no IOPS value is specified, the original IOPS value of the '
                   'volume will be used.***\n'
                   'Requirements: [If original IOPS/GB for the volume is less '
                   'than 0.3, new IOPS/GB must also be less '
                   'than 0.3. If original IOPS/GB for the volume is greater '
                   'than or equal to 0.3, new IOPS/GB for the volume must '
                   'also be greater than or equal to 0.3.]')
@click.option('--new-tier', '-t',
              help='Endurance Storage Tier (IOPS per GB) [only used for '
                   'endurance volumes] ***If no tier is specified, the original tier '
                   'of the volume will be used.***\n'
                   'Requirements: [If original IOPS/GB for the volume is 0.25, '
                   'new IOPS/GB for the volume must also be 0.25. If original IOPS/GB '
                   'for the volume is greater than 0.25, new IOPS/GB '
                   'for the volume must also be greater than 0.25.]',
              type=click.Choice(['0.25', '2', '4', '10']))
@environment.pass_env
def cli(env, volume_id, new_size, new_iops, new_tier):
    """Modify an existing block storage volume."""
    block_manager = SoftLayer.BlockStorageManager(env.client)

    block_volume = block_manager.get_block_volume_details(volume_id)
    block_volume = utils.NestedDict(block_volume)

    storage_type = block_volume['storageType']['keyName'].split('_').pop(0)
    help_message = "For help, try \"slcli block volume-modify --help\"."

    if storage_type == 'ENDURANCE':
        if new_iops is not None:
            raise exceptions.CLIAbort(
                'Invalid option --new-iops for Endurance volume. Please use --new-tier instead.')

        if new_size is None and new_tier is None:
            raise exceptions.CLIAbort(
                'Option --new-size or --new-tier must be specified for modifying an Endurance volume. \n'+
                help_message
            )

    if storage_type == 'PERFORMANCE':
        if new_tier is not None:
            raise exceptions.CLIAbort(
                'Invalid option --new-tier for Performance volume. Please use --new-iops instead.')

        if new_size is None and new_iops is None:
            raise exceptions.CLIAbort(
                'Option --new-size or --new-iops must be specified for modifying a Performance volume. \n' +
                help_message
            )

    if new_tier is not None:
        new_tier = float(new_tier)

    try:
        order = block_manager.order_modified_volume(
            volume_id,
            new_size=new_size,
            new_iops=new_iops,
            new_tier_level=new_tier,
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
