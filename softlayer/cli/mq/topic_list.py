"""List all topics on an account."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting

import click


@click.command()
@click.argument('account-id')
@click.option('--datacenter', help="Datacenter, E.G.: dal05")
@click.option('--network',
              type=click.Choice(['public', 'private']),
              help="Network type")
@environment.pass_env
def cli(env, account_id, datacenter, network):
    """List all topics on an account."""

    manager = softlayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)
    topics = mq_client.get_topics()['items']

    table = formatting.Table(['name'])
    for topic in topics:
        table.add_row([topic['name']])
    return table
