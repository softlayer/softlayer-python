"""Delete a queue or a queued message."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('account-id')
@click.argument('queue-name')
@click.argument('message-id', required=False)
@click.option('--force', is_flag=True, help="Force the deletion of the queue")
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, account_id, queue_name, message_id, force, datacenter, network):
    """Delete a queue or a queued message."""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)

    if message_id:
        mq_client.delete_message(queue_name, message_id)
    else:
        mq_client.delete_queue(queue_name, force)
