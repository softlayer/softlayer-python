"""Updates every subnet with the specified Contact information."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.managers.registration import RegistrationManager


@click.command()
@click.argument('person')
@click.option('--skip', '-s', multiple=True, type=int,
              help='The id of one subnet to skip')
@environment.pass_env
def cli(env, person, skip):
    """Updates every subnet with the specified Contact information."""
    skip_subnet_list = list(skip)
    env.registerClient = RegistrationManager(env.client)
    env.registerClient.update_all(person, skip_subnet_list)
    click.secho("Successfully registered subnets to {}".format(person))
