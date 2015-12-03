"""List all records in a zone."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
# pylint: disable=redefined-builtin


@click.command()
@click.argument('zone')
@click.option('--data', help='Record data, such as an IP address')
@click.option('--record', help='Host record, such as www')
@click.option('--ttl',
              type=click.INT,
              help='TTL value in seconds, such as 86400')
@click.option('--type', help='Record type, such as A or CNAME')
@environment.pass_env
def cli(env, zone, data, record, ttl, type):
    """List all records in a zone."""

    manager = SoftLayer.DNSManager(env.client)
    table = formatting.Table(['id', 'record', 'type', 'ttl', 'data'])

    table.align['ttl'] = 'l'
    table.align['record'] = 'r'
    table.align['data'] = 'l'

    zone_id = helpers.resolve_id(manager.resolve_ids, zone, name='zone')

    records = manager.get_records(zone_id,
                                  record_type=type,
                                  host=record,
                                  ttl=ttl,
                                  data=data)

    for record in records:
        table.add_row([
            record['id'],
            record['host'],
            record['type'].upper(),
            record['ttl'],
            record['data']
        ])

    env.fout(table)
