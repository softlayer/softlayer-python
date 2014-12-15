"""Update DNS record."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import helpers

import click
# pylint: disable=redefined-builtin


@click.command()
@click.argument('zone-id')
@click.option('--by-record', help='Edit by host record, such as www')
@click.option('--by-id', help='Edit a single record by its ID')
@click.option('--data', help='Record data, such as an IP address')
@click.option('--ttl',
              type=click.INT,
              help='TTL value in seconds, such as 86400')
@environment.pass_env
def cli(env, zone_id, by_record, by_id, data, ttl):
    """Update DNS record."""
    manager = softlayer.DNSManager(env.client)
    zone_id = helpers.resolve_id(manager.resolve_ids, zone_id, name='zone')

    results = manager.get_records(zone_id, host=by_record)

    for result in results:
        if by_id and str(result['id']) != by_id:
            continue
        result['data'] = data or result['data']
        result['ttl'] = ttl or result['ttl']
        manager.edit_record(result)
