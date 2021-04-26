"""Add or remove specific subnets access for a user."""
# :license: MIT, see LICENSE for more details.


import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.option('--add/--remove', default=True,
              help="Add or remove access to subnets.")
@click.argument('user', nargs=1, required=True)
@click.argument('subnet', nargs=-1, required=True)
@environment.pass_env
def cli(env, user, add, subnet):
    """Add or remove subnets access for a user."""
    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, user, 'username')
    if add:
        result = mgr.vpn_subnet_add(user_id, subnet)
    else:
        result = mgr.vpn_subnet_remove(user_id, subnet)

    if result:
        click.secho("%s updated successfully" % (user), fg='green')
    else:
        click.secho("Failed to update %s" % (user), fg='red')
