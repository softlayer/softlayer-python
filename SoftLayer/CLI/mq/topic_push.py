"""Push a message into a topic."""
# :license: MIT, see LICENSE for more details.
import sys

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import mq


@click.command()
@click.argument('account-id')
@click.argument('topic-name')
@click.argument('message')
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, account_id, topic_name, message, datacenter, network):
    """Push a message into a topic."""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)

    # the message body comes from the positional argument or stdin
    body = ''
    if message == '-':
        body = sys.stdin.read()
    else:
        body = message
    env.fout(mq.message_table(mq_client.push_topic_message(topic_name, body)))
