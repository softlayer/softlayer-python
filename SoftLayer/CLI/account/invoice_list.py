"""Invoice listing"""
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

    # List invoices

    # invoice id, total recurring, total one time, total other, summary of what was ordered
    # 123, 5$, 0$, 0$, 1 hardware, 2 vsi, 1 storage, 1 vlan