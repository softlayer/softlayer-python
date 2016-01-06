"""Create a new topic."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers
from SoftLayer.CLI import mq


@click.command()
@click.argument('account-id')
@click.argument('topic-name')
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@click.option('--visibility-interval',
              type=click.INT,
              default=30,
              show_default=True,
              help="Time in seconds that messages will re-appear after being "
                   "popped")
@click.option('--expiration',
              type=click.INT,
              default=604800,
              show_default=True,
              help="Time in seconds that messages will live")
@helpers.multi_option('--tag', '-g', help="Tags to add to the topic")
@environment.pass_env
def cli(env, account_id, topic_name, datacenter, network,
        visibility_interval, expiration, tag):
    """Create a new topic."""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)

    topic = mq_client.create_topic(
        topic_name,
        visibility_interval=visibility_interval,
        expiration=expiration,
        tags=tag,
    )
    env.fout(mq.topic_table(topic))
