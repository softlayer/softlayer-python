"""Manages Reserved Capacity."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting



@click.command()
@environment.pass_env
def cli(env):
    """Manages Capacity"""
    print("LIaaaaST")
