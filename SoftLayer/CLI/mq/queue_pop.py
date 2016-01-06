"""Pops a message from a queue."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import mq


@click.command()
@click.argument('account-id')
@click.argument('queue-name')
@click.option('--count',
              default=1,
              show_default=True,
              type=click.INT,
              help="Count of messages to pop")
@click.option('--delete-after',
              is_flag=True,
              help="Remove popped messages from the queue")
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, account_id, queue_name, count, delete_after, datacenter, network):
    """Pops a message from a queue."""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)

    messages = mq_client.pop_messages(queue_name, count)
    formatted_messages = []
    for message in messages['items']:
        formatted_messages.append(mq.message_table(message))

    if delete_after:
        for message in messages['items']:
            mq_client.delete_message(queue_name, message['id'])
    env.fout(formatted_messages)
