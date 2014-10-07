"""Create a zone"""
# :license: MIT, see LICENSE for more details.

import SoftLayer

import click


@click.command()
@click.argument('zone')
def cli(env, zone):
    """Create a zone"""

    manager = SoftLayer.DNSManager(env.client)
    manager.create_zone(zone)
