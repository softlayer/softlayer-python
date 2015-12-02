"""List virtual server credentials."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """List virtual server credentials."""

    manager = SoftLayer.HardwareManager(env.client)
    hardware_id = helpers.resolve_id(manager.resolve_ids,
                                     identifier,
                                     'hardware')
    instance = manager.get_hardware(hardware_id)

    table = formatting.Table(['username', 'password'])
    for item in instance['operatingSystem']['passwords']:
        table.add_row([item['username'], item['password']])
    env.fout(table)
