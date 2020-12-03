"""Registers a Subnet with the specified Contact information"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.registration import RegistrationManager


@click.command()
@click.argument('subnet')
@click.argument('person')
@environment.pass_env
def cli(env, subnet, person):
    """Registers a Subnet with the specified Contact information

    See `slcli registration contacts` for a list of Contact Ids\n
    See `slcli registration show` for a list of Subnet ids
    """
    from pprint import pprint as pp
    registerClient = RegistrationManager(env.client)

    # If there are any failures, this will throw an exception
    registration = registerClient.register(subnet, person)
    
    click.secho("Successfully registered subnet {} to {}".format(subnet, person))
    
