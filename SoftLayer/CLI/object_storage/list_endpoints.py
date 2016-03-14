"""List Object Storage endpoints."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """List object storage endpoints."""

    mgr = SoftLayer.ObjectStorageManager(env.client)
    endpoints = mgr.list_endpoints()

    table = formatting.Table(['datacenter', 'public', 'private'])
    for endpoint in endpoints:
        table.add_row([
            endpoint['datacenter']['name'],
            endpoint['public'],
            endpoint['private'],
        ])

    env.fout(table)
