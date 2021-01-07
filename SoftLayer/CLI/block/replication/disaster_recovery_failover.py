"""Failover an inaccessible file volume to its available replicant volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import exceptions


@click.command(epilog="""Failover an inaccessible block/file volume to its available replicant volume.
If a volume (with replication) becomes inaccessible due to a disaster event, this method can be used to immediately failover to an available replica in another location.
This method does not allow for fail back via the API. To fail back to the original volume after using this method, open a support ticket.
To test failover, use SoftLayer_Network_Storage::failoverToReplicant instead.""")
@click.argument('volume-id')
@click.option('--replicant-id', help="ID of the replicant volume")
@environment.pass_env
def cli(env, volume_id, replicant_id):
    """Failover an inaccessible file volume to its available replicant volume."""
    block_storage_manager = SoftLayer.BlockStorageManager(env.client)

    click.secho("""WARNING : Failover an inaccessible block/file volume to its available replicant volume."""
                """If a volume (with replication) becomes inaccessible due to a disaster event, this method can be used to immediately failover to an available replica in another location."""
                """This method does not allow for fail back via the API."""
                """To fail back to the original volume after using this method, open a support ticket."""
                """To test failover, use SoftLayer_Network_Storage::failoverToReplicant instead.""",fg = 'red' )
   
    if not (formatting.confirm('Are you sure you want to continue?')):
        raise exceptions.CLIAbort('Aborted.')

    block_storage_manager.disaster_recovery_failover_to_replicant(
        volume_id,
        replicant_id
    )
    
    click.echo("Disaster Recovery Failover to replicant is now in progress.")
