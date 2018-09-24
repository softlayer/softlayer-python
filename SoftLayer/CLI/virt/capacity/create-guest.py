"""List Reserved Capacity"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager


from pprint import pprint as pp

@click.command()
@environment.pass_env
def cli(env):
    print("This is where you would create a guest")