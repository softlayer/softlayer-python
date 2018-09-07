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
    """Sets a user's status to CANCEL_PENDING, which will immediately disable the account,

    and will eventually be fully removed from the account by an automated internal process.

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
