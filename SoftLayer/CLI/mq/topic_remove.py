"""Delete a topic."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('account-id')
@click.argument('topic-name')
@click.option('--force', is_flag=True, help="Force the deletion of the queue")
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, account_id, topic_name, force, datacenter, network):
    """Delete a topic."""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)
    mq_client.delete_topic(topic_name, force)
