"""Failover an inaccessible file volume to its available replicant volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import exceptions


@click.command()
@click.argument('volume-id')
@click.option('--replicant-id', help="ID of the replicant volume")
@environment.pass_env
def cli(env, volume_id, replicant_id):
    """Failover an inaccessible file volume to its available replicant volume."""
    block_storage_manager = SoftLayer.BlockStorageManager(env.client)

    click.secho("""WARNING:Disaster Recovery Failover a block volume to the given replicant volume.\n"""
                """* This action cannot be undone\n"""
                """* You will not be able to perform failback to the original\n"""
                """* You cannot failover without replica""",fg = 'red' )
   
    if not (formatting.confirm('Are you sure you want to continue?')):
        raise exceptions.CLIAbort('Aborted.')

    success = block_storage_manager.disaster_recovery_failover_to_replicant(
        volume_id,
        replicant_id
    )
    if success:
        click.echo("Disaster Recovery Failover to replicant is now in progress.")
    else:
        click.echo("Disaster Recovery Failover operation could not be initiated.")
