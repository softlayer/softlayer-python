"""Update DNS record."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers
# pylint: disable=redefined-builtin


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('zone-id')
@click.option('--by-record', help='Edit by host record, such as www')
@click.option('--by-id', help='Edit a single record by its ID')
@click.option('--data', help='Record data, such as an IP address')
@click.option('--ttl',
              type=click.INT,
              help='TTL value in seconds, such as 86400')
@environment.pass_env
def cli(env, zone_id, by_record, by_id, data, ttl):
    """Update DNS record.

    Example::
        slcli dns record-edit ibm.com --by-id 12345678 --data 127.0.0.2 --ttl 3600
        This command edits records under the zone: ibm.com, whose ID is 12345678, \
and sets its data to "127.0.0.2" and ttl to 3600.

        slcli dns record-edit ibm.com --by-record kibana --ttl 3600
        This command edits records under the zone: ibm.com, whose host is "kibana", and sets their ttl all to 3600.
"""
    manager = SoftLayer.DNSManager(env.client)
    zone_id = helpers.resolve_id(manager.resolve_ids, zone_id, name='zone')

    results = manager.get_records(zone_id, host=by_record)

    for result in results:
        if by_id and str(result['id']) != by_id:
            continue
        result['data'] = data or result['data']
        result['ttl'] = ttl or result['ttl']
        manager.edit_record(result)
