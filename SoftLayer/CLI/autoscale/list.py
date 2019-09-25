"""List virtual servers."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.managers.autoscale import AutoScaleManager


@click.command()
@environment.pass_env
def cli(env):
    """List AutoScale Groups."""

    autoscale = AutoScaleManager(env.client)
    groups = autoscale.list()
    print(groups)
    # table = formatting.Table()


    # env.fout(table)
