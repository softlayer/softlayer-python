"""Remove a subscription on a topic."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('account-id')
@click.argument('topic-name')
@click.argument('subscription-id')
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, account_id, topic_name, subscription_id, datacenter, network):
    """Remove a subscription on a topic."""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)
    mq_client.delete_subscription(topic_name, subscription_id)
