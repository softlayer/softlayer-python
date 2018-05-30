"""Enable or Disable specific permissions for a user"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--enable/--disable', default=True,
              help="Enable (DEFAULT) or Disable selected permissions")
@click.option('--permission', '-p', multiple=True, required=True,
              help="Permission keyName to set, multiple instances allowed. Use keyword ALL to select ALL permisssions")
@click.option('--from-user', '-u', default=None, 
              help="Set permissions to match this user's permissions")
@environment.pass_env
def cli(env, identifier, enable, permission, from_user):
    """Enable or Disable specific permissions."""
    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'username')
    result = False
    # TODO, this bit. Make sure from-user and permission/enable are exclusive
    if from_user:
       result = mgr.permissions_from_user(user_id, from_user) 
    if enable:
        result = mgr.add_permissions(user_id, permission)
    else:
        result = mgr.remove_permissions(user_id, permission)

    if result:
        click.secho("Permissions updated successfully: %s" % ", ".join(permission), fg='green')
    else:
        click.secho("Failed to update permissions: %s" % ", ".join(permission), fg='red')
