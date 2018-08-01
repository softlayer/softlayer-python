"""Delete user."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Delete a User

    Example: slcli user delete userId
    """

    mgr = SoftLayer.UserManager(env.client)

    user_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'username')

    user_template = {'userStatusId': 1021}

    result = mgr.edit_user(user_id, user_template)
    if result:
        click.secho("%s deleted successfully" % identifier, fg='green')
    else:
        click.secho("Failed to delete %s" % identifier, fg='red')
