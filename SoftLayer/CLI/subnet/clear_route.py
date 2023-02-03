"""Remove the route of your Account Owned subnets."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Remove the route of your Account Owned subnets."""

    mgr = SoftLayer.NetworkManager(env.client)

    subnet = mgr.clear_route(identifier)

    if subnet:
        click.secho("The transaction to clear the route is created, routes will be updated in one or two minutes.")
    else:
        raise exceptions.CLIAbort('Failed to clear the route for the subnet.')
