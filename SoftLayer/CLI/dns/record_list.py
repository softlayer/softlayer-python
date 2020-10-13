"""List all records in a zone."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
# pylint: disable=redefined-builtin, redefined-argument-from-local


@click.command()
@click.argument('zone')
@click.option('--data', help='Record data, such as an IP address')
@click.option('--record', help='Host record, such as www')
@click.option('--ttl', type=click.INT,
              help='TTL value in seconds, such as 86400')
@click.option('--type', 'record_type', help='Record type, such as A or CNAME')
@environment.pass_env
def cli(env, zone, data, record, ttl, record_type):
    """List all records in a zone."""

    manager = SoftLayer.DNSManager(env.client)
    table = formatting.Table(['id', 'record', 'type', 'ttl', 'data'])
    table.align = 'l'

    zone_id = helpers.resolve_id(manager.resolve_ids, zone, name='zone')

    records = manager.get_records(zone_id, record_type=record_type, host=record, ttl=ttl, data=data)

    for the_record in records:
        table.add_row([
            the_record.get('id'),
            the_record.get('host', ''),
            the_record.get('type').upper(),
            the_record.get('ttl'),
            the_record.get('data')
        ])

    env.fout(table)
