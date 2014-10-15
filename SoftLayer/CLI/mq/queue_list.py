"""List SoftLayer Message Queue Endpoints"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

import click


@click.command()
@click.argument('account-id')
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, account_id, datacenter, network):
    """List SoftLayer Message Queue Endpoints"""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)

    queues = mq_client.get_queues()['items']

    table = formatting.Table(['name',
                              'message_count',
                              'visible_message_count'])
    for queue in queues:
        table.add_row([queue['name'],
                       queue['message_count'],
                       queue['visible_message_count']])
    return table
