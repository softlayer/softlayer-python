"""Cancel a subnet."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel a subnet."""

    mgr = SoftLayer.NetworkManager(env.client)
    subnet_id = helpers.resolve_id(mgr.resolve_subnet_ids, identifier,
                                   name='subnet')

    if not (env.skip_confirmations or formatting.no_going_back(subnet_id)):
        raise exceptions.CLIAbort('Aborted')

    mgr.cancel_subnet(subnet_id)
