"""Remove block storage subnets for the given host id."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('access_id')
@click.option('--subnet-id', multiple=True, type=int,
              help="ID of the subnets to remove; e.g.: --subnet-id 1234")
@environment.pass_env
def cli(env, access_id, subnet_id):
    """Remove block storage subnets for the given host id.

    access_id is the allowed_host_id from slcli block access-list
    """
    subnets_id = list(subnet_id)
    block_manager = SoftLayer.BlockStorageManager(env.client)
    removed_subnets = block_manager.remove_subnets_from_acl(access_id,
                                                            subnets_id)

    for subnet in removed_subnets:
        click.echo("Successfully removed subnet id: " + str(subnet) +
                   ' to allowed host id: ' + str(access_id) + '.')

    failed_to_remove_subnets = list(set(subnets_id) - set(removed_subnets))
    for subnet in failed_to_remove_subnets:
        click.echo("Failed to remove subnet id: " + str(subnet) +
                   ' to allowed host id: ' + str(access_id) + '.')
