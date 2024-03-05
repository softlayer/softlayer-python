"""Allows to create, remove or refresh user's API authentication key."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--add', is_flag=True, default=False,
              help="Create an user's API authentication key.")
@click.option('--remove', is_flag=True, default=False,
              help="Remove an user's API authentication key.")
@click.option('--refresh', is_flag=True, default=False,
              help="Refresh an user's API authentication key.")
@environment.pass_env
def cli(env, identifier, add, remove, refresh):

    """Allows to create, remove or refresh user's API authentication key.

    Each user can only have a single API key.
    """

    options = {
        '--add': add,
        '--remove': remove,
        '--refresh': refresh,
    }

    if not any(options.values()):
        raise exceptions.CLIAbort(f'At least one option is required: [{",".join(options.keys())}]')

    if sum(options.values()) > 1:
        raise exceptions.CLIAbort(f'Can only specify one option of [{",".join(options.keys())}]')

    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'username')

    if remove or refresh:
        mgr.remove_api_authentication_key(user_id)
        click.secho('Successfully removed API authentication key', fg='green')

    if add or refresh:
        api_authentication_key = mgr.add_api_authentication_key(user_id)
        click.secho(f'Successfully added. New API Authentication Key: {api_authentication_key}', fg='green')
