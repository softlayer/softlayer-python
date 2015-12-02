"""Create a subscription on a topic."""
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
@click.option('--sub-type',
              type=click.Choice(['http', 'queue']),
              help="Type of endpoint")
@click.option('--queue-name', help="Queue name. Required if --type is queue")
@click.option('--http-method', help="HTTP Method to use if --type is http")
@click.option('--http-url',
              help="HTTP/HTTPS URL to use. Required if --type is http")
@click.option('--http-body',
              help="HTTP Body template to use if --type is http")
@environment.pass_env
def cli(env, account_id, topic_name, datacenter, network, sub_type, queue_name,
        http_method, http_url, http_body):
    """Create a subscription on a topic."""

    manager = SoftLayer.MessagingManager(env.client)
    mq_client = manager.get_connection(account_id,
                                       datacenter=datacenter, network=network)
    if sub_type == 'queue':
        subscription = mq_client.create_subscription(topic_name, 'queue',
                                                     queue_name=queue_name)
    elif sub_type == 'http':
        subscription = mq_client.create_subscription(
            topic_name,
            'http',
            method=http_method,
            url=http_url,
            body=http_body,
        )
    env.fout(mq.subscription_table(subscription))
