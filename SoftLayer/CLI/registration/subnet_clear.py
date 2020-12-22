"""Clear an existing subnet registration."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.managers.registration import RegistrationManager


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Clear an existing subnet registration."""

    env.registerClient = RegistrationManager(env.client)

    if not (env.skip_confirmations or formatting.no_going_back(identifier)):
        raise exceptions.CLIAbort('Aborted')

    registration = env.registerClient.clear(identifier)

    if registration is None:
        raise exceptions.CLIAbort(
            'Could not clear the subnet registration because no active registration found for this Subnet'
        )

    if registration:
        click.echo('The subnet registration with id %s was successfully cleared' % identifier)
    else:
        click.echo('Unable to clear the subnet registration with id %s' % identifier)
