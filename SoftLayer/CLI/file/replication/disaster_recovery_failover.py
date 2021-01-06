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
    file_storage_manager = SoftLayer.FileStorageManager(env.client)

    click.secho("""WARNING : Disaster Recovery Failover should not be performed unless data center for the primary volume is unreachable.\n"""
                """* This action cannot be undone\n"""
                """* You will not be able to perform failback to the original without support intervention\n"""
                """* You cannot failover without replica""",fg = 'red' )
    
    if not (formatting.confirm('Are you sure you want to continue?')):
        raise exceptions.CLIAbort('Aborted.')

    success = file_storage_manager.disaster_recovery_failover_to_replicant(
        volume_id,
        replicant_id
    )
    if success:
        click.echo("Disaster Recovery Failover to replicant is now in progress.")
    else:
        click.echo("Disaster Recovery Failover operation could not be initiated.")