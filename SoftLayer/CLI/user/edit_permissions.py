"""Enable or Disable specific permissions for a user"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--enable/--disable', default=True,
              help="Enable or Disable selected permissions")
@click.option('--permission', '-p', multiple=True,
              help="Permission keyName to set, multiple instances allowed.")
@environment.pass_env
def cli(env, identifier, enable, permission):
    """Enable or Disable specific permissions."""

    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'username')
    result = False
    if enable:
        result = mgr.add_permissions(user_id, permission)
    else:
        result = mgr.remove_permissions(user_id, permission)

    if result:
        click.secho("Permissions updated successfully: %s" % ", ".join(permission), fg='green')
    else:
        click.secho("Failed to update permissions: %s" % ", ".join(permission), fg='red')
