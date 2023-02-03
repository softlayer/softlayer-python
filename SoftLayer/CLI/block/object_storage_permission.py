"""Display permission details for a cloud object storage."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('object_id')
@environment.pass_env
def cli(env, object_id):
    """Display permission details for a cloud object storage."""

    block_manager = SoftLayer.BlockStorageManager(env.client)

    cloud = block_manager.get_network_message_delivery_accounts(object_id)
    end_points = block_manager.get_end_points(object_id)

    table = formatting.Table(['Name', 'Value'])

    table_credentials = formatting.Table(['Id', 'Access Key ID', 'Secret Access Key', 'Description'])

    for credential in cloud.get('credentials'):
        table_credentials.add_row([credential.get('id'),
                                   credential.get('username'),
                                   credential.get('password'),
                                   credential['type']['description']])

    table_url = formatting.Table(['Region',
                                  'Location',
                                  'Type',
                                  'URL'])
    for end_point in end_points:
        table_url.add_row([end_point.get('region') or '',
                           end_point.get('location') or '',
                           end_point.get('type'),
                           end_point.get('url'), ])

    table.add_row(['UUID', cloud.get('uuid')])
    table.add_row(['Credentials', table_credentials])
    table.add_row(['EndPoint URL´s', table_url])
    env.fout(table)
