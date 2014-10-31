"""Add resource record."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers

import click
# pylint: disable=redefined-builtin


@click.command()
@click.argument('zone')
@click.argument('record')
@click.argument('type')
@click.argument('data')
@click.option('--ttl',
              type=click.INT,
              default=7200,
              help='TTL value in seconds, such as 86400')
@environment.pass_env
def cli(env, zone, record, type, data, ttl):
    """Add resource record."""

    manager = SoftLayer.DNSManager(env.client)
    zone_id = helpers.resolve_id(manager.resolve_ids, zone, name='zone')
    manager.create_record(zone_id, record, type, data, ttl=ttl)
