"""List images."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers

from pprint import pprint as pp


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier, ):
    """List images."""

    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'image')

    user = mgr.get_user(user_id)
    # pp(users)
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    for key in user:
        table.add_row([key, user[key]])

    env.fout(table)

