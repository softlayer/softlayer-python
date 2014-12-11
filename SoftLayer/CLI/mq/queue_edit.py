"""Modify a queue."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers
from SoftLayer.CLI import mq


import click


@click.command()
@click.argument('account-id')
@click.argument('queue-name')
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@click.option('--visibility-interval',
              type=click.INT,
              default=30,
              help="Time in seconds that messages will re-appear after being "
                   "popped")
@click.option('--expiration',
              type=click.INT,
              default=604800,
              help="Time in seconds that messages will live")
@helpers.multi_option('--tag', '-g', help="Tags to add to the queue")
@environment.pass_env
def cli(env, account_id, queue_name, datacenter, network, visibility_interval,
        expiration, tag):
    """Modify a queue."""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)

    queue = mq_client.modify_queue(
        queue_name,
        visibility_interval=visibility_interval,
        expiration=expiration,
        tags=tag,
    )
    return mq.queue_table(queue)
