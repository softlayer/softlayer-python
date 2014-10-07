"""Update DNS record."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment

import click
# pylint: disable=redefined-builtin


@click.command()
@click.argument('record_id')
@click.option('--record', help='Host record, such as www')
@click.option('--data', help='Record data, such as an IP address')
@click.option('--ttl',
              type=click.INT,
              help='TTL value in seconds, such as 86400')
@click.option('--type', help='Record type, such as A or CNAME')
@environment.pass_env
def cli(env, record_id, record, data, ttl, type):
    """Update DNS record."""
    manager = SoftLayer.DNSManager(env.client)
    result = manager.get_record(record_id)
    result['host'] = record or result['record']
    result['ttl'] = ttl or result['ttl']
    result['type'] = type or result['type']
    result['data'] = data or result['data']
    manager.edit_record(result)
