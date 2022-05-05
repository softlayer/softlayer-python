"""List Placement Groups"""

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_placement import PlacementManager as PlacementManager
from SoftLayer import utils


@click.command(cls=SLCommand)
@environment.pass_env
def cli(env):
    """List placement groups."""
    manager = PlacementManager(env.client)
    result = manager.list()
    table = formatting.Table(
        ["Id", "Name", "Backend Router", "Rule", "Guests", "Created"],
        title="Placement Groups"
    )
    for group in result:
        table.add_row([
            utils.lookup(group, 'id'),
            utils.lookup(group, 'name'),
            utils.lookup(group, 'backendRouter', 'hostname'),
            utils.lookup(group, 'rule', 'name'),
            utils.lookup(group, 'guestCount'),
            utils.lookup(group, 'createDate')
        ])

    env.fout(table)
