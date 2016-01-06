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

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    instance = vsi.get_instance(vs_id)

    table = formatting.Table(['username', 'password'])
    for item in instance['operatingSystem']['passwords']:
        table.add_row([item['username'], item['password']])
    env.fout(table)
