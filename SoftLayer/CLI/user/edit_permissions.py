"""Enable or Disable specific permissions for a user"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils

from pprint import pprint as pp


@click.command()
@click.argument('identifier')
@click.option('--enable/--disable', default=True,
                help="Enable or Disable selected permissions")
@click.option('--permission', '-p', multiple=True,
                help="Permission keyName to set, multiple instances allowed.")
@environment.pass_env
def cli(env, identifier, enable, permission):
    """Enable or Disable specific permissions for a user"""
    
    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'username')
    object_mask = "mask[id,permissions,isMasterUserFlag]"
    if enable:
        result = mgr.add_permissions(identifier, permission)
        click.secho("Permissions added successfully: %s" % ", ".join(permission), fg='green')
    else:
        result = mgr.remove_permissions(identifier, permission)
        click.secho("Permissions removed successfully: %s" % ", ".join(permission), fg='green')

