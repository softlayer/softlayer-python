"""Display details for a specified cloud object storage."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('object_id')
@environment.pass_env
def cli(env, object_id):
    """Display details for a cloud object storage."""

    block_manager = SoftLayer.BlockStorageManager(env.client)

    cloud = block_manager.get_volume_details(object_id)
    bucket = block_manager.get_buckets(object_id)

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    table.add_row(['Id', cloud.get('id')])
    table.add_row(['Username', cloud.get('username')])
    table.add_row(['Name Service Resource', cloud['serviceResource']['name']])
    table.add_row(['Type Service Resource', cloud['serviceResource']['type']['type']])
    table.add_row(['Datacenter', cloud['serviceResource']['datacenter']['name']])
    table.add_row(['Storage type', cloud['storageType']['keyName']])
    table.add_row(['Bytes Used', formatting.b_to_gb(bucket[0]['bytesUsed'])])
    table.add_row(['Bucket name', bucket[0]['name']])

    env.fout(table)
