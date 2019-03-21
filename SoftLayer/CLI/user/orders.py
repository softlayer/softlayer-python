"""Users order details"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """Lists each user and the servers they ordered"""

    # Table = [user name, fqdn, cost]
    # maybe print ordered storage / network bits
    # if given a single user id, just print detailed info from that user
