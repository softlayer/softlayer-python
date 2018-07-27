"""List NAS account credentials."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """List NAS account credentials."""

    nw_mgr = SoftLayer.NetworkManager(env.client)
    result = nw_mgr.get_nas_credentials(identifier)
    table = formatting.Table(['username', 'password'])
    table.add_row([result.get('username', 'None'),
                   result.get('password', 'None')])
    env.fout(table)
