"""Account Maintance manager"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()

@environment.pass_env
def cli(env):
    """Summary and acknowledgement of upcoming and ongoing maintenance"""

    # Print a list of all on going maintenance 

    # Allow ack all, or ack specific maintenance