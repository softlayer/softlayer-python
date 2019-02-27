"""Account Summary page"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()

@environment.pass_env
def cli(env):
    """Prints some various bits of information about an account"""

    #TODO
    # account info
    # # of servers, vsi, vlans, ips, per dc?
    # next invoice details
    # upcoming cancelations?
    # tickets and events upcoming

