"""Order a file storage volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


CONTEXT_SETTINGS = {'token_normalize_func': lambda x: x.upper()}


@click.command(cls=SoftLayer.CLI.command.SLCommand, context_settings=CONTEXT_SETTINGS)
@click.option('--storage-type', required=True, type=click.Choice(['performance', 'endurance']),
              help='Type of file storage volume')
@click.option('--size', type=int, required=True,
              help='Size of file storage volume in GB')
@click.option('--iops', type=int,
              help="""Performance Storage IOPs. Options vary based on storage size.
[required for storage-type performance]""")
@click.option('--tier', type=click.Choice(['0.25', '2', '4', '10']),
              help='Endurance Storage Tier (IOP per GB) [required for storage-type endurance]')
@click.option('-l', '--location', required=True,
              help='Datacenter short name (e.g.: dal09)')
@click.option('--snapshot-size', type=int,
              help='Optional parameter for ordering snapshot '
              'space along with endurance file storage; specifies '
              'the size (in GB) of snapshot space to order')
@click.option('--service-offering',
              help="""The service offering package to use for placing the order.
[optional, default is \'storage_as_a_service\']. enterprise and performance are depreciated""",
              default='storage_as_a_service',
              type=click.Choice([
                  'storage_as_a_service',
                  'enterprise',
                  'performance']))
@click.option('--billing', type=click.Choice(['hourly', 'monthly']), default='monthly',
              help="Optional parameter for Billing rate (default to monthly)")
@click.option('--force', default=False, is_flag=True, help="Force order file storage volume without confirmation")
@environment.pass_env
def cli(env, storage_type, size, iops, tier,
        location, snapshot_size, service_offering, billing, force):
    """Order a file storage volume.

    Example::
        slcli file volume-order --storage-type performance --size 1000 --iops 4000 -d dal09
        This command orders a performance volume with size is 1000GB, IOPS is 4000, located at dal09.

        slcli file volume-order --storage-type endurance --size 500 --tier 4 -d dal09 --snapshot-size 500
        This command orders an endurance volume with size is 500GB, tier level is 4 IOPS per GB,\
located at dal09 with an additional snapshot space size of 500GB

    Valid size and iops options can be found here:
    https://cloud.ibm.com/docs/FileStorage/index.html#provisioning-considerations
    """
    file_manager = SoftLayer.FileStorageManager(env.client)
    storage_type = storage_type.lower()

    if not force:
        if not (env.skip_confirmations or
                formatting.confirm("This action will incur charges on your account. Continue?")):
            raise exceptions.CLIAbort('Aborted')

    hourly_billing_flag = False
    if billing.lower() == "hourly":
        hourly_billing_flag = True

    if service_offering != 'storage_as_a_service':
        click.secho(f'{service_offering} is a legacy storage offering', fg='red')
        if hourly_billing_flag:
            raise exceptions.CLIAbort(
                'Hourly billing is only available for the storage_as_a_service service offering'
            )

    order = {}
    if storage_type == 'performance':
        if iops is None:
            raise exceptions.CLIAbort('Option --iops required with Performance')

        if service_offering == 'performance' and snapshot_size is not None:
            raise exceptions.CLIAbort(
                '--snapshot-size is not available for performance service offerings. '
                'Use --service-offering storage_as_a_service'
            )

        try:
            order = file_manager.order_file_volume(
                storage_type=storage_type,
                location=location,
                size=size,
                iops=iops,
                snapshot_size=snapshot_size,
                service_offering=service_offering,
                hourly_billing_flag=hourly_billing_flag
            )
        except ValueError as ex:
            raise exceptions.ArgumentError(str(ex))

    if storage_type == 'endurance':
        if tier is None:
            raise exceptions.CLIAbort(
                'Option --tier required with Endurance in IOPS/GB [0.25,2,4,10]'
            )

        try:
            order = file_manager.order_file_volume(
                storage_type=storage_type,
                location=location,
                size=size,
                tier_level=float(tier),
                snapshot_size=snapshot_size,
                service_offering=service_offering,
                hourly_billing_flag=hourly_billing_flag
            )
        except ValueError as ex:
            raise exceptions.ArgumentError(str(ex))

    if 'placedOrder' in order.keys():
        click.echo(f"Order #{order['placedOrder']['id']} placed successfully!")
        for item in order['placedOrder']['items']:
            click.echo(" > %s" % item['description'])
        click.echo(
            f"\nYou may run \"slcli file volume-list --order {order['placedOrder']['id']}\" to find this file "
            "volume after it is ready.")
    else:
        click.echo("Order could not be placed! Please verify your options and try again.")
