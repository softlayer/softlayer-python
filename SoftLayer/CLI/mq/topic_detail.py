"""Detail a topic."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import mq


@click.command()
@click.argument('account-id')
@click.argument('topic-name')
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, account_id, topic_name, datacenter, network):
    """Detail a topic."""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)
    topic = mq_client.get_topic(topic_name)
    subscriptions = mq_client.get_subscriptions(topic_name)
    tables = []
    for sub in subscriptions['items']:
        tables.append(mq.subscription_table(sub))
    env.fout([mq.topic_table(topic), tables])
