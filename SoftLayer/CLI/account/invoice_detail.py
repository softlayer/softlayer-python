"""Invoice details"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()

@environment.pass_env
def cli(env):
    """Invoices and all that mess"""

    # Print a detail of upcoming invoice, or specified invoice

    # export to pdf/excel