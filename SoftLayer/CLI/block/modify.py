"""Modify an existing block storage volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


CONTEXT_SETTINGS = {'token_normalize_func': lambda x: x.upper()}


@click.command(cls=SoftLayer.CLI.command.SLCommand, context_settings=CONTEXT_SETTINGS)
@click.argument('volume-id')
@click.option('--new-size', '-c',
              type=int,
              help='New Size of block volume in GB. ***If no size is given, the original size of volume is used.***\n'
                   'Potential Sizes: [20, 40, 80, 100, 250, 500, 1000, 2000, 4000, 8000, 12000]\n'
                   'Minimum: [the original size of the volume]')
@click.option('--new-iops', '-i',
              type=int,
              help='Performance Storage IOPS, between 100 and 6000 in multiples of 100 [only for performance volumes] '
                   '***If no IOPS value is specified, the original IOPS value of the volume will be used.***')
@click.option('--new-tier', '-t',
              help='Endurance Storage Tier (IOPS per GB) [only for endurance volumes] Classic Choices: '
                   '***If no tier is specified, the original tier of the volume will be used.***',
              type=click.Choice(['0.25', '2', '4', '10']))
@environment.pass_env
def cli(env, volume_id, new_size, new_iops, new_tier):
    """Modify an existing block storage volume. Choices.

    Valid size and iops options can be found here:
        https://cloud.ibm.com/docs/BlockStorage/index.html#provisioning-considerations
        https://cloud.ibm.com/docs/BlockStorage?topic=BlockStorage-orderingBlockStorage&interface=cli

    Example::

        slcli block volume-modify 12345678 --new-size 1000 --new-iops 4000
        This command modify a volume 12345678 with size is 1000GB, IOPS is 4000.

        slcli block volume-modify 12345678 --new-size 500 --new-tier 4
        This command modify a volume 12345678 with size is 500GB, tier level is 4 IOPS per GB.
"""

    block_manager = SoftLayer.BlockStorageManager(env.client)

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
        click.echo(f"Order #{order['placedOrder']['id']} placed successfully!")
        for item in order['placedOrder']['items']:
            click.echo(" > %s" % item['description'])
    else:
        click.echo("Order could not be placed! Please verify your options and try again.")
