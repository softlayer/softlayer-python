"""Remove block storage subnets for the given host id."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('access_id', type=int)
@click.option('--subnet-id', multiple=True, type=int,
              help="ID of the subnets to remove; e.g.: --subnet-id 1234")
@environment.pass_env
def cli(env, access_id, subnet_id):
    """Remove block storage subnets for the given host id.

    access_id is the host_id obtained by: slcli block access-list <volume_id>

    SoftLayer_Account::iscsiisolationdisabled must be False to use this command
    """
    try:
        subnet_ids = list(subnet_id)
        block_manager = SoftLayer.BlockStorageManager(env.client)
        removed_subnets = block_manager.remove_subnets_from_acl(access_id, subnet_ids)

        for subnet in removed_subnets:
            message = f"Successfully removed subnet id: {subnet} for allowed host id: {access_id}"
            click.echo(message)

        failed_to_remove_subnets = list(set(subnet_ids) - set(removed_subnets))
        for subnet in failed_to_remove_subnets:
            message = f"Failed to remove subnet id: {subnet} for allowed host id: {access_id}"
            click.echo(message)

    except SoftLayer.SoftLayerAPIError as ex:
        message = f"Unable to remove subnets.\nReason: {ex.faultString}"
        click.echo(message)
