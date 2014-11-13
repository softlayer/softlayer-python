"""Cancel a subnet."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import exceptions
from softlayer.cli import formatting
from softlayer.cli import helpers

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel a subnet."""

    mgr = softlayer.NetworkManager(env.client)
    subnet_id = helpers.resolve_id(mgr.resolve_subnet_ids, identifier,
                                   name='subnet')

    if env.skip_confirmations or formatting.no_going_back(subnet_id):
        mgr.cancel_subnet(subnet_id)
    else:
        raise exceptions.CLIAbort('Aborted')
