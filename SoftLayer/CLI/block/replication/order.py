"""Order a block storage replica volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers
from SoftLayer import utils


CONTEXT_SETTINGS = {'token_normalize_func': lambda x: x.upper()}


@click.command(cls=SoftLayer.CLI.command.SLCommand, context_settings=CONTEXT_SETTINGS)
@click.argument('volume_id')
@click.option('--datacenter', '-d',
              help='Short name of the datacenter for the replica (e.g.: dal09)',
              required=True)
@click.option('--iops', '-i',
              help='Performance Storage IOPs, between 100 and 6000 in multiples of 100. If no IOPS value is specified,'
              ' the IOPS value of the original volume will be used.',
              type=int)
@click.option('--os-type', '-o',
              help='Operating System Type (eg. LINUX) of the primary volume for '
              'which a replica is ordered [optional].',
              type=click.Choice([
                  'HYPER_V',
                  'LINUX',
                  'VMWARE',
                  'WINDOWS_2008',
                  'WINDOWS_GPT',
                  'WINDOWS',
                  'XEN']))
@click.option('--snapshot-schedule', '-s',
              help='Snapshot schedule to use for replication. Options are: '
              'HOURLY, DAILY, WEEKLY',
              required=True,
              type=click.Choice(['HOURLY', 'DAILY', 'WEEKLY']))
@click.option('--tier', '-t',
              help='Endurance Storage Tier (IOPS per GB) of the primary volume for which a replica is ordered '
              '[optional]. If no tier is specified, the tier of the original volume will be used',
              type=click.Choice(['0.25', '2', '4', '10']))
@environment.pass_env
def cli(env, volume_id, snapshot_schedule, datacenter, tier, os_type, iops):
    """Order a block storage replica volume."""
    block_manager = SoftLayer.BlockStorageManager(env.client)
    block_volume_id = helpers.resolve_id(block_manager.resolve_ids, volume_id, 'Block Volume')

    if tier is not None:
        tier = float(tier)

    if iops is not None:
        if iops < 100 or iops > 6000:
            raise exceptions.ArgumentError(f"Invalid value for '--iops' / '-i': '{iops}' is not one "
                                           "of between 100 and 6000.")
        if iops % 100 != 0:
            raise exceptions.ArgumentError(f"Invalid value for '--iops' / '-i': '{iops}' is not a multiple of 100.")

    try:
        order = block_manager.order_replicant_volume(
            block_volume_id,
            snapshot_schedule=snapshot_schedule,
            location=datacenter,
            tier=tier,
            os_type=os_type,
            iops=iops
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
