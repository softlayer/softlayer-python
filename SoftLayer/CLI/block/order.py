"""Order a block storage volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


CONTEXT_SETTINGS = {'token_normalize_func': lambda x: x.upper()}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--storage-type',
              help='Type of block storage volume',
              type=click.Choice(['performance', 'endurance']),
              required=True)
@click.option('--size',
              type=int,
              help='Size of block storage volume in GB. Permitted Sizes:\n'
                   '20, 40, 80, 100, 250, 500, 1000, 2000, 4000, 8000, 12000',
              required=True)
@click.option('--iops',
              type=int,
              help='Performance Storage IOPs,'
              ' between 100 and 6000 in multiples of 100'
              '  [required for storage-type performance]')
@click.option('--tier',
              help='Endurance Storage Tier (IOP per GB)'
              '  [required for storage-type endurance]',
              type=click.Choice(['0.25', '2', '4', '10']))
@click.option('--os-type',
              help='Operating System',
              type=click.Choice([
                  'HYPER_V',
                  'LINUX',
                  'VMWARE',
                  'WINDOWS_2008',
                  'WINDOWS_GPT',
                  'WINDOWS',
                  'XEN']),
              required=True)
@click.option('--location',
              help='Datacenter short name (e.g.: dal09)',
              required=True)
@click.option('--snapshot-size',
              type=int,
              help='Optional parameter for ordering snapshot '
              'space along with endurance block storage; specifies '
              'the size (in GB) of snapshot space to order')
@environment.pass_env
def cli(env, storage_type, size, iops, tier, os_type,
        location, snapshot_size):
    """Order a block storage volume."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    storage_type = storage_type.lower()

    if storage_type == 'performance':
        if iops is None:
            raise exceptions.CLIAbort(
                'Option --iops required with Performance')

        if iops < 100 or iops > 6000:
            raise exceptions.CLIAbort(
                'Option --iops must be between 100 and 6000, inclusive')

        if iops % 100 != 0:
            raise exceptions.CLIAbort(
                'Option --iops must be a multiple of 100'
            )

        if snapshot_size is not None:
            raise exceptions.CLIAbort(
                'Option --snapshot-size not allowed for performance volumes.'
                'Snapshots are only available for endurance storage.'
            )

        try:
            order = block_manager.order_block_volume(
                storage_type='performance_storage_iscsi',
                location=location,
                size=int(size),
                iops=iops,
                os_type=os_type
            )
        except ValueError as ex:
            raise exceptions.ArgumentError(str(ex))

    if storage_type == 'endurance':
        if tier is None:
            raise exceptions.CLIAbort(
                'Option --tier required with Endurance in IOPS/GB '
                '[0.25,2,4,10]'
            )

        try:
            order = block_manager.order_block_volume(
                storage_type='storage_service_enterprise',
                location=location,
                size=int(size),
                tier_level=float(tier),
                os_type=os_type,
                snapshot_size=snapshot_size
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
