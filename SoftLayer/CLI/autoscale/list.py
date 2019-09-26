"""List Autoscale groups."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.managers.autoscale import AutoScaleManager
from SoftLayer import utils

from pprint import pprint as pp 

@click.command()
@environment.pass_env
def cli(env):
    """List AutoScale Groups."""

    autoscale = AutoScaleManager(env.client)
    groups = autoscale.list()
    # print(groups)
    # pp(groups)
    table = formatting.Table(["Id", "Name", "Status", "Min/Max", "Running"])

    for group in groups:
        status = utils.lookup(group, 'status', 'name')
        min_max = "{}/{}".format(group.get('minimumMemberCount', '-'), group.get('maximumMemberCount'), '-')
        table.add_row([
            group.get('id'), group.get('name'), status, min_max, group.get('virtualGuestMemberCount')
        ])


    env.fout(table)
