"""Push a message into a queue."""
# :license: MIT, see LICENSE for more details.
import sys

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import mq


@click.command()
@click.argument('account-id')
@click.argument('queue-name')
@click.argument('message')
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, account_id, queue_name, message, datacenter, network):
    """Push a message into a queue."""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)
    body = ''
    if message == '-':
        body = sys.stdin.read()
    else:
        body = message
    env.fout(mq.message_table(mq_client.push_queue_message(queue_name, body)))
