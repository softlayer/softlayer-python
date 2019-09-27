"""List Autoscale groups."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.autoscale import AutoScaleManager
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):
    """List AutoScale Groups."""

    autoscale = AutoScaleManager(env.client)
    groups = autoscale.list()

    table = formatting.Table(["Id", "Name", "Status", "Min/Max", "Running"])
    table.align['Name'] = 'l'
    for group in groups:
        status = utils.lookup(group, 'status', 'name')
        min_max = "{}/{}".format(group.get('minimumMemberCount'), group.get('maximumMemberCount'))
        table.add_row([
            group.get('id'), group.get('name'), status, min_max, group.get('virtualGuestMemberCount')
        ])

    env.fout(table)
