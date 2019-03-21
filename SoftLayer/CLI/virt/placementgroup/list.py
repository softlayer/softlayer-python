"""List Placement Groups"""

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_placement import PlacementManager as PlacementManager


@click.command()
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
            group['id'],
            group['name'],
            group['backendRouter']['hostname'],
            group['rule']['name'],
            group['guestCount'],
            group['createDate']
        ])

    env.fout(table)
